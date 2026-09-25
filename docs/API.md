# API Reference

Base URL (local dev): `http://localhost:8000` · (prod server): `http://127.0.0.1:8080`

All responses are `application/json` and share a common envelope. Keys are
**camelCase**. See [ARCHITECTURE.md](ARCHITECTURE.md) for internals.

## Endpoints

| Method | Path                    | Purpose                             | Rate limit          |
| ------ | ----------------------- | ----------------------------------- | ------------------- |
| GET    | `/`                     | 1 random law (default locale)       | 90/min (+ defaults) |
| GET    | `/{number}`             | Up to `number` laws (1–50), default locale | 90/min (+ defaults) |
| GET    | `/{locale}`             | 1 random law in that locale         | 90/min (+ defaults) |
| GET    | `/{locale}/{number}`    | Up to `number` laws in that locale  | 90/min (+ defaults) |
| GET    | `/health`               | Liveness probe                      | 90/min (+ defaults) |
| GET    | `/env?key=…`            | Whitelisted env vars (secret-gated) | 10/min (+ defaults) |
| GET    | `/flush`                | Flush the Redis cache               | 10/min (+ defaults) |

Available locales come from `db/data.<locale>.json` (`en`, `it`); the default
locale is `en`.

Trailing slashes are accepted everywhere (`/it/` == `/it`, `/it/2/` == `/it/2`).

Global defaults (apply to every route): `90 per minute`, `50000 per day`,
keyed by client IP.

---

### `GET /`, `GET /{number}`, `GET /{locale}`, and `GET /{locale}/{number}`

Returns one or more random Murphy's Laws. Without a locale the default
(`en`) is served.

**Path parameters**

- `locale` — dataset language (e.g. `en`, `it`). An unknown locale → **404**.
- `number` — how many laws to return.
  - Non-integer (e.g. `/it/abc`) → **400**.
  - Below `1` is clamped to 1; above `50` (`MAX_LAWS`) is clamped to 50 (`/999` → 50 laws, **200**).

Note: a bare `/en` works because a single unknown segment matches `/{number}`
and is dispatched to the locale handler. A single segment that is neither a
known locale nor an integer (e.g. `/foo`) → **404**.

**Response `200`**

```json
{
  "code": 200,
  "status": "success",
  "returnCount": 2,
  "totalCount": 912,
  "locale": "en",
  "data": [
    { "law": "Anything that can go wrong will go wrong." },
    {
      "law": "If there is a possibility of several things going wrong, the one that will cause the most damage will be the one to go wrong.",
      "corollary": {
        "law": "If there is a worse time for something to go wrong, it will happen then."
      }
    }
  ]
}
```

Each law is `{ "law": string }`, optionally with `corollary: { "law": string }`.
`totalCount` is the size of the requested locale's dataset.

**Extra headers**

| Header          | Meaning                                     |
| --------------- | ------------------------------------------- |
| `X-Count`       | Number of laws returned (== `returnCount`)  |
| `X-Total-Count` | Total laws in the dataset (== `totalCount`) |
| `X-Locale`      | Locale of the returned laws (== `locale`)   |

---

### `GET /health`

Runs the `py-healthcheck` health check (reports app health). Responds `200` with
its own JSON body when healthy.

---

### `GET /env?key={SHOW_ENV_KEY}`

Returns the environment variables whitelisted in `SAFE_ENV_VARS`
(`AUTHOR`, `CACHE_ENABLED`, `CACHE_HOST`, `CACHE_PORT`, `CACHE_TTL`, `VERCEL_ENV`).

- Missing key, wrong key, or empty/unset `SHOW_ENV_KEY` → **403**.
- Never exposes `SHOW_ENV_KEY` or `CACHE_PASSWORD`.

**Response `200`**

```json
{
  "code": 200,
  "status": "success",
  "data": {
    "AUTHOR": "iamgnlc",
    "CACHE_ENABLED": "1",
    "CACHE_HOST": "…",
    "CACHE_PORT": "…",
    "CACHE_TTL": "…",
    "VERCEL_ENV": "production"
  }
}
```

---

### `GET /flush`

Flushes **all** keys from the Redis cache (`FLUSHALL`).

**Response `200`**

```json
{ "code": 200, "status": "success", "flush": true }
```

Calls Redis synchronously but is **best-effort**: if Redis is unreachable the
failure is logged and the endpoint still returns `200` with `"flush": false`.
It is the only endpoint that talks to Redis on the request path.

---

## Common Response Headers (all endpoints)

| Header                             | Value                                                                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `X-Author`                         | `AUTHOR` env var                                                                                                         |
| `X-Robots-Tag`                     | `noindex`                                                                                                                |
| `Access-Control-Allow-Origin`      | `*`                                                                                                                      |
| `Access-Control-Allow-Credentials` | `true`                                                                                                                   |
| `Access-Control-Allow-Methods`     | `GET, OPTIONS, PATCH, DELETE, POST, PUT`                                                                                 |
| `Access-Control-Allow-Headers`     | `X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version` |

## Error Format

All errors use the same envelope, produced by the `Message` class:

| Status | Body                                                                   |
| ------ | ---------------------------------------------------------------------- || 400 | `{ "code": 400, "status": "bad request" }` — non-integer count on a valid resource, e.g. `/it/abc` |
| 403 | `{ "code": 403, "status": "not authorized" }` — `/env` auth failure |
| 404 | `{ "code": 404, "status": "not found" }` — any unknown path: single-segment (`/foo`) or multi-segment (`/foo/bar`, `/xx/2`) |
| 429    | `{ "code": 429, "status": "too many requests" }` — rate limit exceeded |

Example:

```json
{ "code": 404, "status": "not found" }
```

## Quick Examples

```sh
# One random law (default locale)
curl -s http://localhost:8000/

# Five laws (inspect count headers)
curl -si http://localhost:8000/5 | grep -iE "x-count|x-total|x-locale"

# One law in English
curl -s http://localhost:8000/en

# Two laws in Italian
curl -s http://localhost:8000/it/2

# Health
curl -s http://localhost:8000/health

# Env (requires SHOW_ENV_KEY to be set server-side)
curl -s "http://localhost:8000/env?key=$SHOW_ENV_KEY"

# Flush cache
curl -s http://localhost:8000/flush
```
