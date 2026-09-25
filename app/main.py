import atexit
import json
import logging
import os
import random
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

import redis
from camel_converter import dict_to_camel
from colorama import Fore, Style
from flask import Flask, Response, abort, request
from healthcheck import HealthCheck

from app import DEFAULT_LOCALE, ENV, MAX_LAWS, SAFE_ENV_VARS, SHOW_ENV_KEY
from app.utils import (
    Cache,
    Message,
    available_locales,
    default_headers,
    load_data,
    print_logo,
    rate_limiter,
    validate,
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
# "/path" and "/path/" are equivalent on every route (e.g. /it == /it/).
app.url_map.strict_slashes = False
cache_executor = ThreadPoolExecutor(max_workers=5)
atexit.register(lambda: cache_executor.shutdown(wait=True))
if ENV == "production":  # pragma: no cover
    app.config["DEBUG"] = False

if ENV == "development":
    print_logo()

data = {locale: load_data(locale) for locale in available_locales()}
limiter = rate_limiter(app)

health_check = HealthCheck()
message = Message()
cache = Cache()


def show_laws(laws, locale=DEFAULT_LOCALE):
    meta_data = {
        "return_count": len(laws),
        "total_count": len(data[locale]),
        "locale": locale,
    }
    custom_headers = {
        "X-Count": meta_data["return_count"],
        "X-Total-Count": meta_data["total_count"],
        "X-Locale": locale,
    }
    headers = {**default_headers(), **custom_headers}

    payload = {**message.success, **dict_to_camel(meta_data), "data": laws}

    return send_response(payload=payload, headers=headers)


def send_response(payload, status: int = 200, headers: dict | None = None):
    if headers is None:
        headers = default_headers()
    response = Response(
        json.dumps(payload),
        mimetype="application/json",
        headers=headers,
        status=status,
    )

    return response


# Show whitelisted env vars only if authorized.
@app.route("/env")
@limiter.limit("10 per minute")
def env():
    def invalid_key(key):
        return key is None or key != SHOW_ENV_KEY or SHOW_ENV_KEY == ""

    key = request.args.get("key")
    if invalid_key(key):
        abort(403)

    safe_env = {k: os.environ.get(k, "") for k in SAFE_ENV_VARS}
    return send_response({**message.success, "data": safe_env})


# Health check.
@app.route("/health")
@limiter.limit("90 per minute")
def health():
    return health_check.run()


@app.route("/flush")
@limiter.limit("10 per minute")
def flush():
    # Best-effort: never let an unreachable Redis turn into a 500.
    flushed = False
    try:
        flushed = cache.flush
    except redis.RedisError as e:
        logger.error("Cache flush failed: %s", e)
    return send_response({**message.success, "flush": flushed})


# Show law(s).
# ``/<locale>`` (e.g. /en) is intentionally NOT a route: it matches the
# ``/<number>`` rule (both are single segments) and is dispatched by main().
@app.route("/")
@app.route("/<number>")
@limiter.limit("90 per minute")
def main(number: str = "1"):
    # ``/<number>`` also matches single-segment locales like /en; when the
    # segment is a known locale, serve it with the default count.
    if number in data:
        locale, number = number, "1"
    else:
        locale = DEFAULT_LOCALE
        # A single segment that is neither a known locale nor an integer
        # (e.g. /foo) identifies no resource → 404, not 400.
        if validate(number, 1, MAX_LAWS) is False:
            abort(404)

    return serve_laws(locale, number)


@app.route("/<locale>/<number>")
@limiter.limit("90 per minute")
def main_locale(locale: str, number: str):
    # An unknown locale means the resource does not exist (404), e.g.
    # /foo/bar; a known locale with an invalid count is a 400.
    if locale not in data:
        abort(404)

    return serve_laws(locale, number)


def serve_laws(locale: str, number: str):
    number = validate(number, 1, MAX_LAWS)

    if number is False:
        abort(400)

    laws = random.sample(data[locale], number)

    # Push to cache if enabled and responding.
    if cache.is_enabled and cache.ping:
        cache_executor.submit(cache.update, laws)

    return show_laws(laws, locale=locale)


@app.errorhandler(400)
def bad_request(e):
    payload = message.bad_request
    return send_response(payload=payload, status=payload["code"])


@app.errorhandler(404)
def page_not_found(e):
    payload = message.not_found
    return send_response(payload=payload, status=payload["code"])


@app.errorhandler(403)
def not_authorized(e):
    payload = message.not_authorized
    return send_response(payload=payload, status=payload["code"])


@app.errorhandler(429)
def too_many_requests(e):
    payload = message.too_many_requests
    return send_response(payload=payload, status=payload["code"])


def sigint(signal, frame):
    print(Fore.RED + "Server terminated." + Style.RESET_ALL)
    sys.exit(0)


signal.signal(signal.SIGINT, sigint)
