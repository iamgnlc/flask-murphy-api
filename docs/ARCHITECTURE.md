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
      db/data.<locale>.json  app/utils/*                redis (optional)
      (912 laws × 2 locales,  validate / Message /
       loaded once at        default_headers /
       import, immutable     rate_limiter / Cache
       in-memory tuples)
```

There is no database, no ORM, and no authentication middleware. The entire
domain is "sample N items from an immutable in-memory list and serialize them."

## Module Map

| Module                         | Responsibility     | Key facts                                                                                                                                                                                            |
| ------------------------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/__init__.py`              | Config constants   | Reads all env vars once via dotenv; exports `MAX_LAWS=50`, `SAFE_ENV_VARS`, `__version__`; `ENV` falls back to `"development"` when `VERCEL_ENV` is unset. Everything else imports config from here. |
| `app/main.py`                  | The app itself     | All 4 routes, all error handlers, response assembly. Vercel serverless entry point.                                                                                                                  |
| `app/utils/load_data.py`       | Dataset loading    | Resolves `db/data.<locale>.json` relative to its own file (3 levels up); `load_data(locale)` returns an immutable `tuple`, `available_locales()` discovers locales from filenames.                |
| `app/utils/validate.py`        | Input coercion     | `int()` conversion; `False` on `ValueError`; clamps into `[min, max]` instead of rejecting.                                                                                                          |
| `app/utils/cache.py`           | Redis integration  | Lazy-connecting `redis.Redis`; memoized ping; pipeline writes; content-addressed keys.                                                                                                               |
| `app/utils/message.py`         | Response envelopes | Single source of truth for `{code, status}` payloads.                                                                                                                                                |
| `app/utils/default_headers.py` | Common headers     | `X-Author`, `X-Robots-Tag: noindex`, permissive CORS.                                                                                                                                                |
| `app/utils/rate_limiter.py`    | Rate limiting      | flask-limiter, keyed by remote address, **in-memory** storage.                                                                                                                                       |
| `app/utils/print_logo.py`      | Dev cosmetics      | ASCII logo when `ENV == "development"`.                                                                                                                                                              |
| `server.py`                    | Waitress host      | Hardcoded `127.0.0.1:8080`, optional port via `sys.argv[1]`. Not used on Vercel.                                                                                                                     |

## Request Lifecycle: `GET /<number>` or `GET /<locale>/<number>`

1. **Rate limit** — route limit `90 per minute` stacks on defaults (`90 per minute`, `50000 per day`), keyed by client IP, stored in-process.
2. **Dispatch** — `/` and single segments (`/2`, `/en`) hit `main()`; `/en/2`-style two-segment paths hit `main_locale()`. A single segment naming a known locale is served as a locale request with count 1; anything else is a count for the default locale.
3. **Validate** — `validate(number, 1, MAX_LAWS)` coerces the count segment to `int`. Non-numeric → `False` → `abort(400)`. Out-of-range values are **clamped** (`/999` → 50, `/-5` → 1). An unknown locale (`/xx` or `/xx/2`) or any other path identifying no resource (e.g. `/foo`) → `abort(404)`.
4. **Sample** — `random.sample(data[locale], number)` picks unique laws from the locale's in-memory tuple (all locales loaded once at import).
5. **Cache (fire-and-forget)** — if `CACHE_ENABLED` and Redis answers `ping` (memoized for 5 s), the laws are pushed to Redis on a 5-worker `ThreadPoolExecutor` so response latency never depends on Redis. Write failures are logged, never raised. Keys are content-addressed (`murphy:<md5(sorted JSON)>`), so the same law in different locales naturally maps to different keys.
6. **Serialize** — payload merges `Message.success` + camelCased metadata (`returnCount`, `totalCount`, `locale`) + `data`; response merges `default_headers()` + `X-Count` + `X-Total-Count` + `X-Locale`.
7. **Respond** — `Response(json.dumps(payload), mimetype="application/json", status=200)`.

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

`load_data(locale)` returns a `tuple` per locale and runs at import time for every file matching `db/data.<locale>.json` (via `available_locales()`). The datasets are effectively build-time constants; hot-reloading is out of scope. Adding a language is dropping a `db/data.<locale>.json` file and (optionally) no code changes. On Vercel the JSON files are bundled with the function.

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
- `tests/utils/` — pure unit tests for `validate`, `Message`, `default_headers`, `load_data` (including locale discovery).
- No Redis server or network is required to run the suite: `make test`.

## Deployment

- **Vercel:** `vercel.json` builds `app/main.py` with `@vercel/python` and maps
  `/(.*)` → it. `ENV`/`VERCEL_ENV` is set by the platform; Redis creds and other
  secrets are Vercel environment variables (never committed).
- **Self-hosted / local prod:** `make start` → Waitress on `127.0.0.1:8080`
  (port overridable: `python server.py 9000`). Put a reverse proxy in front for
  TLS/public exposure — Waitress binds to loopback only.
- **CI:** GitHub Actions runs `ruff check .` + `pytest` on every push (Python 3.12).
