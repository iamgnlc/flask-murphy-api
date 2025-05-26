import json
import random
import signal
import sys

from camel_converter import dict_to_camel
from colorama import Fore, Style
from flask import Flask, Response, request, abort
from healthcheck import HealthCheck, EnvironmentDump
# from threading import Thread # Line removed
from concurrent.futures import ThreadPoolExecutor # Added
import atexit # Added

from app import MAX_LAWS, SHOW_ENV_KEY, ENV
from app.utils import load_data, print_logo, validate, default_headers, rate_limiter
from app.utils import Cache, Message

app = Flask(__name__)
cache_executor = ThreadPoolExecutor(max_workers=5) # Added
atexit.register(lambda: cache_executor.shutdown(wait=True)) # Added
if ENV == "production":
    app.config["DEBUG"] = False

if ENV == "development":
    print_logo()

data = load_data()
limiter = rate_limiter(app)

environment_dump = EnvironmentDump()
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


# Show env vars only if authorized.
@app.route("/env")
def env():
    def invalid_key(key):
        return key is None or key != SHOW_ENV_KEY or SHOW_ENV_KEY == ""

    key = request.args.get("key")
    if invalid_key(key):
        abort(403)

    return environment_dump.run()


# Health check.
@app.route("/health")
def health():
    return health_check.run()


@app.route("/flush")
def flush():
    return send_response({**message.success, "flush": cache.flush})


# Show law(s).
@app.route("/")
@app.route("/<number>")
def main(number: int = 1):
    number = validate(number, 1, MAX_LAWS)

    if number is False:
        abort(404)

    laws = random.sample(data, number)

    # Push to cache if enabled and responding.
    if cache.is_enabled and cache.ping:
        cache_executor.submit(cache.update, laws) # Changed

    return show_laws(laws)


@app.errorhandler(404)
def page_not_found(e):
    return send_response(
        payload=message.not_found,
        status=message.not_found["code"],
    )


@app.errorhandler(403)
def not_authorized(e):
    return send_response(
        payload=message.not_authorized,
        status=message.not_authorized["code"],
    )


@app.errorhandler(429)
def too_many_requests(e):
    return send_response(
        payload=message.too_many_requests,
        status=message.too_many_requests["code"],
    )


def sigint(signal, frame):
    print(Fore.RED + "Server terminated." + Style.RESET_ALL)
    sys.exit(0)


signal.signal(signal.SIGINT, sigint)
