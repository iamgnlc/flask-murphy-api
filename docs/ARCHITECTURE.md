# Architecture

How **flask-murphy-api** is structured and why. For endpoint-level detail see
[API.md](API.md); for agent-oriented working instructions see [../AGENTS.md](../AGENTS.md).

## High-Level View

```
                 ┌──────────────────────────────┐
   Vercel ───────►  app/main.py (Flask WSGI app)  ◄─────── server.py (Waitress, local/prod)
   (vercel.json   └──────────────┬───────────────┘
    maps / → main.py)            │
              ┌──────────────────┼───────────────────────┐
              ▼                  ▼                       ▼
      db/data.json         app/utils/*                redis (optional)
      (912 laws,           validate / Message /       murphy:<md5> keys,
       loaded once at      default_headers /          written async, TTL =
       import, immutable   rate_limiter / Cache       CACHE_TTL
       in-memory tuple)
```

There is no database, no ORM, and no authentication middleware. The entire
domain is "sample N items from an immutable in-memory list and serialize them."

## Module Map

| Module | Responsibility | Key facts |
|---|---|---|
| `app/__init__.py` | Config constants | Reads all env vars once via dotenv; exports `MAX_LAWS=50`, `SAFE_ENV_VARS`, `__version__`; `ENV` falls back to `"development"` when `VERCEL_ENV` is unset. Everything else imports config from here. |
| `app/main.py` | The app itself | All 4 routes, all error handlers, response assembly. Vercel serverless entry point. |
| `app/utils/load_data.py` | Dataset loading | Resolves `db/data.json` relative to its own file (3 levels up), returns an immutable `tuple`. |
| `app/utils/validate.py` | Input coercion | `int()` conversion; `False` on `ValueError`; clamps into `[min, max]` instead of rejecting. |
| `app/utils/Cache.py` | Redis integration | Lazy-connecting `redis.Redis`; memoized ping; pipeline writes; content-addressed keys. |
| `app/utils/Message.py` | Response envelopes | Single source of truth for `{code, status}` payloads. |
| `app/utils/default_headers.py` | Common headers | `X-Author`, `X-Robots-Tag: noindex`, permissive CORS. |
| `app/utils/rate_limiter.py` | Rate limiting | flask-limiter, keyed by remote address, **in-memory** storage. |
| `app/utils/print_logo.py` | Dev cosmetics | ASCII logo when `ENV == "development"`. |
| `server.py` | Waitress host | Hardcoded `127.0.0.1:8080`, optional port via `sys.argv[1]`. Not used on Vercel. |

## Request Lifecycle: `GET /<number>`

1. **Rate limit** — route limit `90 per minute` stacks on defaults (`90 per minute`, `50000 per day`), keyed by client IP, stored in-process.
2. **Validate** — `validate(number, 1, MAX_LAWS)` coerces the path segment to `int`. Non-numeric → `False` → `abort(400)`. Out-of-range values are **clamped** (`/999` → 50, `/-5` → 1).
3. **Sample** — `random.sample(data, number)` picks unique laws from the in-memory tuple (loaded once at import).
4. **Cache (fire-and-forget)** — if `CACHE_ENABLED` and Redis answers `ping` (memoized for 5 s), the laws are pushed to Redis on a 5-worker `ThreadPoolExecutor` so response latency never depends on Redis. Write failures are logged, never raised.
5. **Serialize** — payload merges `Message.success` + camelCased metadata (`returnCount`, `totalCount`) + `data`; response merges `default_headers()` + `X-Count` + `X-Total-Count`.
6. **Respond** — `Response(json.dumps(payload), mimetype="application/json", status=200)`.

Errors never leak internals: 400/403/404/429 are converted to the canonical
envelope by module-level `@app.errorhandler` handlers using the `Message` class.

## Design Decisions

### Cache: content-addressed, best-effort, non-blocking
- **Why async writes?** The cache is an optimization, not a source of truth. A slow/down Redis must never slow down or fail a quote request.
- **Why `murphy:<md5(sorted JSON)>`?** Keys are deterministic per law, so repeated caching of the same law deduplicates instead of accumulating garbage; there is no lookup path in the API today (the cache is write-oriented, presumably for analytics/consumers), which is why `/flush` exists as the only cache-management endpoint.
- **Why the 5-second memoized ping?** Redis availability is checked on every law request; without memoization that would add a round-trip per request. Failures are logged and retried after `PING_TTL = 5` seconds.
- **Pipeline writes** batch all laws of a request into one round-trip, each with expiry `ex=CACHE_TTL`.

### Rate limiting: in-memory by design
`storage_uri="memory://"` keeps the app dependency-free and serverless-friendly.
Consequences: limits are per-process/per-instance (not global), and they reset
on deploy or restart. If strict global limits are ever needed, swap the storage
URI to a shared Redis — the `Limiter` construction is isolated in
`rate_limiter.py` precisely to make that a one-line change.

### Immutable data, loaded once
`load_data()` returns a `tuple` and runs at import time. The dataset is
effectively a build-time constant; hot-reloading it is out of scope. On Vercel
the JSON is bundled with the function.

### Single-file app, thin utilities
All routing/wiring lives in `app/main.py`; utilities are importable, pure-ish
functions/classes with no Flask dependencies (except `rate_limiter`). This
keeps the unit tests in `tests/utils/` free of app context.

## Configuration Flow

```
.env / process env
      │ python-dotenv (app/__init__.py)
      ▼
AUTHOR · SHOW_ENV_KEY · CACHE_* · VERCEL_ENV
      │ imported by
      ├─► main.py      (ENV → debug/logo behavior)
      ├─► Cache.py     (connection + TTL + enabled flag)
      ├─► default_headers.py (AUTHOR)
      └─► /env route   (SAFE_ENV_VARS whitelist only)
```

`ENV` comes from `VERCEL_ENV` (`production` | `preview` | `development`), which is
set by the Vercel platform. Locally it defaults to `"development"`, so the dev
logo prints and the app behaves like a local dev server; on Vercel `production`
forces `DEBUG=False`.

## Testing Strategy

- `tests/test_routes.py` — integration tests through `app.test_client()`; covers every route, error handler, clamping, and headers. `/flush` is tested with `cache` mocked; the `/env` test branches on whether `SHOW_ENV_KEY` is set so it passes with or without secrets.
- `tests/test_cache.py` — `redis.Redis` is fully patched; verifies ping memoization/TTL refresh, pipeline writes, empty-input no-op, and `ConnectionError` swallowing.
- `tests/utils/` — pure unit tests for `validate`, `Message`, `default_headers`, `load_data`.
- No Redis server or network is required to run the suite: `make test`.

## Deployment

- **Vercel:** `vercel.json` builds `app/main.py` with `@vercel/python` and maps
  `/(.*)` → it. `ENV`/`VERCEL_ENV` is set by the platform; Redis creds and other
  secrets are Vercel environment variables (never committed).
- **Self-hosted / local prod:** `make start` → Waitress on `127.0.0.1:8080`
  (port overridable: `python server.py 9000`). Put a reverse proxy in front for
  TLS/public exposure — Waitress binds to loopback only.
- **CI:** GitHub Actions runs `ruff check .` + `pytest` on every push (Python 3.12).
