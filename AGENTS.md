# AGENTS.md

> Instructions and context for AI coding agents working in this repository.
> Read this before making changes. Details live in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/API.md](docs/API.md).

## What This Project Is

**flask-murphy-api** (v1.0.0) — a small, production-deployed JSON REST API that
returns random **Murphy's Law** quotes. It is intentionally minimal: one Flask
app module, a handful of pure utility functions, per-locale JSON data files
(912 laws each in `db/data.en.json` and `db/data.it.json`), and an optional
Redis cache. It runs locally under Waitress and deploys to **Vercel** as a
serverless Python function.

Typical usage: `GET /` returns 1 random law in the default locale (`en`);
`GET /5` returns 5; `GET /en` returns 1 English law; `GET /it/2` returns 2
Italian laws.

**Stack:** Python ≥ 3.12, Flask 3, flask-limiter, redis-py, waitress, camel-converter,
colorama, py-healthcheck, python-dotenv. Tests: pytest + pytest-cov. Tooling: ruff (lint), black (format).

## Commands

| Task | Command | Notes |
|---|---|---|
| Install deps | `make install` | `pip install -r requirements-dev.txt` (runtime + dev tools) |
| Run dev server | `make dev` | Flask dev server, debug on, port **8000** (from `.flaskenv`) |
| Run prod server | `make start` | Waitress on `127.0.0.1:8080`; optional port: `python server.py 9000` |
| Run tests | `make test` | `pytest --verbosity=1 --cov` (testpaths: `tests/`) |
| Lint | `make lint` | `ruff check .` — CI fails on lint errors |
| Format | `make format` | `black .` |
| Freeze deps | `make freeze` | Regenerates `requirements.txt` (runtime) and `requirements-dev.txt` (full) from the venv |
| Clean caches | `make clean` | Runs `./clean.sh` (removes `__pycache__`, `.pytest_cache`, `.ruff_cache`) |

There is **no Docker** and no database migration tooling. CI (`.github/workflows/ci-cd.yml`)
runs two jobs on every push (Python 3.12): `build` (ruff → pytest, installs `requirements-dev.txt`)
and `smoke-test` (installs runtime-only `requirements.txt`, boots `server.py`, and curls `/health`, `/`, `/5`, and a 404 path).

## Project Layout

```
app/
  __init__.py        # Constants: env vars, MAX_LAWS=50, SAFE_ENV_VARS, __version__
  main.py            # THE Flask app: all routes, error handlers, wiring
  utils/
    load_data.py     # Reads db/data.<locale>.json into immutable tuples; available_locales()
    validate.py      # Coerces/clamps the ?count path param; False on ValueError
    cache.py         # Redis wrapper: ping (memoized 5s), flush, content-keyed writes
    message.py       # Canonical response envelopes per status code
    default_headers.py  # X-Author, X-Robots-Tag, CORS headers
    rate_limiter.py  # flask-limiter config (in-memory storage)
    print_logo.py    # Dev-only ASCII logo
db/
  data.en.json       # 912 laws (English): {"law": str, "corollary"?: {"law": str}}
  data.it.json       # 912 laws (Italian): same structure
server.py            # Waitress entrypoint for local/prod (NOT used by Vercel)
tests/
  test_routes.py     # Integration tests via Flask test_client
  test_cache.py      # Cache tests (redis.Redis fully mocked)
  utils/             # Unit tests for validate, Message, headers, load_data
requirements.txt     # Runtime deps only (frozen)
requirements-dev.txt # Dev env (frozen): runtime + pytest, pytest-cov, coverage, ruff
vercel.json          # Maps all routes → app/main.py (Vercel serverless entry)
.flaskenv            # FLASK_RUN_PORT=8000
```

## Architecture in One Paragraph

`app/main.py` builds the Flask app at import time: it loads every locale's
quote data once (`load_data(locale)` for each `available_locales()`),
configures a `Limiter`, and instantiates `Message`, `Cache`, and a 5-worker
`ThreadPoolExecutor` for async cache writes. `GET /<locale>/<number>` (and the
bare `/<number>` form, which uses the default locale) validates/clamps the
requested count (1–50), samples randomly from the locale's in-memory tuple,
fires a fire-and-forget cache write when Redis is enabled and reachable, and
returns a camelCase JSON envelope that includes `locale` plus custom headers
(`X-Locale`, `X-Count`, `X-Total-Count`). Single-segment locale paths (`/en`)
are dispatched by the `/<number>` handler since they match that route; unknown
locales (`/xx`, `/xx/2`) and any other unknown path 404. Errors (400/403/404/429)
are handled centrally and returned in the same envelope. There is no ORM, no
auth (except a shared-secret query param on `/env`), and no persistent state
besides the optional Redis cache.

## Response Contract (do not break)

All endpoints return JSON in this shape (keys camelCase via `camel_converter`):

```json
{
  "code": 200,
  "status": "success",
  "returnCount": 1,
  "totalCount": 912,
  "locale": "en",
  "data": [{ "law": "Anything that can go wrong will go wrong." }]
}
```

Every response also carries headers from `default_headers()` (`X-Author`,
`X-Robots-Tag: noindex`, permissive CORS) plus `X-Count`, `X-Total-Count`, and
`X-Locale` on law endpoints. Status messages come only from the `Message` class — never
hardcode status strings in routes.

## Environment Variables

Loaded from `.env` via python-dotenv in `app/__init__.py` (`.env` is gitignored — never commit or echo its contents):

| Variable | Purpose |
|---|---|
| `AUTHOR` | Sent as `X-Author` header; also exposed via `/env` |
| `SHOW_ENV_KEY` | Shared secret required as `?key=` on `/env` (empty/absent ⇒ always 403) |
| `CACHE_HOST` / `CACHE_PORT` / `CACHE_PASSWORD` | Redis connection |
| `CACHE_TTL` | Expiry (seconds) for cached law keys |
| `CACHE_ENABLED` | `"1"`/`"0"`-style flag; `Cache.is_enabled` does `bool(int(...))` |
| `VERCEL_ENV` | Read as `ENV`; `production` forces `DEBUG=False`, `development` prints the logo. Unset locally. |

`SAFE_ENV_VARS` whitelists which of these `/env` may ever return (never includes
`SHOW_ENV_KEY` or `CACHE_PASSWORD`).

## Conventions & Gotchas

- **Dependency management:** exact `==` pins. `pyproject.toml` is the declaration of record (runtime → `[project].dependencies`, dev tools → `[project.optional-dependencies].dev`); `requirements.txt` (runtime only) and `requirements-dev.txt` (full freeze) are for reproducible installs — CI installs `requirements-dev.txt`. Regenerate both with `make freeze` after changing `pyproject.toml`; hand-edits to the requirements files are lost on the next freeze.
- **`six` is a hidden requirement:** `py-healthcheck` imports `six` without declaring it. The pin exists only for that — don't remove it or the app fails at import.
- **Lint must pass:** `ruff check .` gates CI. Note `ignore-init-module-imports = true` in `pyproject.toml`.
- **`ENV` defaults to `"development"` locally:** it comes from `VERCEL_ENV`, which only the Vercel platform sets (`production`/`preview`/`development`). Locally the dev logo prints; on Vercel `production` forces `DEBUG=False`.
- **Rate limits are in-memory** (`storage_uri="memory://"`): per-process, reset on restart, not shared across Vercel instances. Route-level limits (90/min laws+health, 10/min `/env` and `/flush`) stack on the defaults (90/min, 50000/day).
- **Cache writes are asynchronous** via `ThreadPoolExecutor` and swallow `redis.ConnectionError` — request latency never depends on Redis, and Redis being down never 500s the main route.
- **Cache keys are content-addressed:** `murphy:<md5 of sorted JSON>` — the same law always maps to the same key (dedup by design).
- **`Cache.ping` is memoized for 5 s** (`PING_TTL`) to avoid hammering Redis.
- **`/flush` is best-effort:** it calls `flushall()` synchronously, but failures are caught, logged, and returned as `200` with `"flush": false` — an unreachable Redis never produces a 500.
- **`validate()` clamps rather than rejects:** `/999` returns 50 laws (200); only non-integer input returns `False` → 400 (e.g. `/it/abc`).
- **Routing — unknown paths 404:** a single segment that is neither a known locale nor an integer (`/foo`) 404s (the handler checks before validation), as do unknown two-segment paths like `/xx/2` or `/foo/bar`. The CI smoke test and `test_get_unknown_single_segment_returns_404` rely on this.
- **`app.url_map.strict_slashes = False`** (set in `app/main.py`): trailing slashes are accepted on every route (`/it/` == `/it`). Remove it and `/it/` starts 404ing.
- **Path param is a string:** Flask passes `/<number>` as `str`; the route signature is `number: str = "1"` and `validate()` does the `int()` coercion. Don't change the hint to `int` — the value arrives as a string.
- **Data is loaded once at import** into per-locale tuples; edits to `db/data.<locale>.json` require a process restart. Keep the JSON structure `{law, corollary?}` intact.
- **Locales are discovered from filenames:** dropping `db/data.<locale>.json` into `db/` adds a language with no code changes. `DEFAULT_LOCALE` (`app/__init__.py`) controls what `/` and `/<number>` serve. `/en` matches `/<number>`, so the handler dispatches on known locales; unknown single segments (e.g. `/foo`) 404 and unknown two-segment paths (`/xx/2`) 404.
- **Tests mock Redis entirely** (`@patch("app.utils.cache.redis.Redis")`); no Redis server is needed to run the suite. The `/env` test conditionally asserts based on whether `SHOW_ENV_KEY` is set — keep it working in both cases.
- **Vercel entry point is `app/main.py`** (see `vercel.json`), not `server.py`. `server.py` exists only for non-serverless hosting; its port comes from `sys.argv[1]`, default 8080, host is hardcoded `127.0.0.1`.
- **`app/main.py` runs module-level side effects** (data load, limiter, cache, executor, signal handler) at import — importing it in tests triggers all of this. Be mindful when adding import-time work.

## Definition of Done

1. `make lint` passes.
2. `make test` passes (add/adjust tests for behavior changes — route changes go in `tests/test_routes.py`, cache behavior in `tests/test_cache.py`, pure utilities in `tests/utils/`).
3. Response envelope, headers, and status messages stay consistent with `Message` / `default_headers`.
4. New env vars: added to `app/__init__.py`, and to `SAFE_ENV_VARS` **only if** they are safe to expose via `/env`.
5. No secrets in code, commits, or docs.
