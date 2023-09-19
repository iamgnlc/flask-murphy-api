import json
import random
import signal
import sys

from colorama import Fore, Style
from flask import Flask, Response, request
from healthcheck import HealthCheck, EnvironmentDump
from threading import Thread

from app import AUTHOR, MAX_LAWS, SHOW_ENV_KEY
from app.utils import load_data, print_logo, validate
from app.utils import Cache, Error

app = Flask(__name__)

print_logo()

data = load_data()

default_headers = {
    "X-Author": AUTHOR,
    "X-Robots-Tag": "noindex",
}

environment_dump = EnvironmentDump()
health_check = HealthCheck()
error = Error()
cache = Cache()


def show_laws(laws):
    custom_headers = {
        "X-Count": len(laws),
        "X-Total-Count": len(data),
    }
    headers = {**default_headers, **custom_headers}

    return send_response(payload=laws, headers=headers)


def send_response(payload, status: int = 200, headers=default_headers):
    response = Response(
        json.dumps(payload), mimetype="application/json", headers=headers, status=status
    )

    return response


# Show env vars only if authorized.
@app.route("/env")
def env():
    key = request.args.get("key")
    if key is None or key != SHOW_ENV_KEY:
        return send_response(
            payload=error.not_authorized(),
            status=403,
        )

    return environment_dump.run()


# Health check.
@app.route("/health")
def health():
    return health_check.run()


@app.route("/flush")
def flush():
    return send_response({"flush": cache.flush()})


# Show law(s).
@app.route("/")
@app.route("/<number>")
def main(number: int = 1):
    number = validate(number, 1, MAX_LAWS)

    if number is False:
        return send_response(
            payload=error.not_found(),
            status=404,
        )

    laws = random.sample(data, number)

    # Push to cache if enabled and working.
    if cache.is_enabled() and cache.ping():
        Thread(
            target=cache.update,
            args=(laws,),
        ).start()

    return show_laws(laws)


# Catch 404.
@app.errorhandler(404)
def page_not_found(e):
    return send_response(
        payload=error.not_found(),
        status=404,
    )


def sigint(signal, frame):
    print(Fore.RED + "Server terminated." + Style.RESET_ALL)
    sys.exit(0)


signal.signal(signal.SIGINT, sigint)
