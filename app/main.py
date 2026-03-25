import json
import os
import random
import signal
import sys

from camel_converter import dict_to_camel
from colorama import Fore, Style
from flask import Flask, Response, request, abort
from healthcheck import HealthCheck
from concurrent.futures import ThreadPoolExecutor
import atexit

from app import MAX_LAWS, SHOW_ENV_KEY, ENV, SAFE_ENV_VARS
from app.utils import load_data, print_logo, validate, default_headers, rate_limiter
from app.utils import Cache, Message

app = Flask(__name__)
cache_executor = ThreadPoolExecutor(max_workers=5)
atexit.register(lambda: cache_executor.shutdown(wait=True))
if ENV == "production":  # pragma: no cover
    app.config["DEBUG"] = False

if ENV == "development":
    print_logo()

data = load_data()
limiter = rate_limiter(app)

health_check = HealthCheck()
message = Message()
cache = Cache()


def show_laws(laws):
    meta_data = {
        "return_count": len(laws),
        "total_count": len(data),
    }
    custom_headers = {
        "X-Count": meta_data["return_count"],
        "X-Total-Count": meta_data["total_count"],
    }
    headers = {**default_headers(), **custom_headers}

    payload = {**message.success, **dict_to_camel(meta_data), "data": laws}

    return send_response(payload=payload, headers=headers)


def send_response(payload, status: int = 200, headers=default_headers()):
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
    return send_response({**message.success, "flush": cache.flush})


# Show law(s).
@app.route("/")
@app.route("/<number>")
@limiter.limit("90 per minute")
def main(number: int = 1):
    number = validate(number, 1, MAX_LAWS)

    if number is False:
        abort(400)

    laws = random.sample(data, number)

    # Push to cache if enabled and responding.
    if cache.is_enabled and cache.ping:
        cache_executor.submit(cache.update, laws)

    return show_laws(laws)


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
