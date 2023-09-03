import json
import random
import signal
import sys

from flask import Flask, Response, request
from colorama import Fore, Style

from app import AUTHOR, MAX_LAWS, SHOW_ENV_KEY, CACHE_ENABLED
from app.utils import load_data, print_logo, show_env, validate, update_cache
from app.utils import not_found, not_authorized

app = Flask(__name__)

print_logo()

data = load_data()

default_headers = {
    "X-Author": AUTHOR,
    "X-Robots-Tag": "noindex",
}


def show_laws(laws):
    custom_headers = {
        "X-Count": len(laws),
        "X-Total-Count": len(data),
    }
    headers = {**default_headers, **custom_headers}

    return send_response(payload=laws, headers=headers)


def send_response(payload, status=200, headers=default_headers):
    response = Response(
        json.dumps(payload), mimetype="application/json", headers=headers, status=status
    )

    return response


# Show env vars only if authorized.
@app.route("/env")
def env():
    key = request.args.get("key")
    if key is None or key != SHOW_ENV_KEY:
        return send_response(payload=not_authorized(), status=403)

    return send_response(payload=show_env())


# Show law(s).
@app.route("/")
@app.route("/<number>")
def main(number=1):
    number = validate(number, 1, MAX_LAWS)

    if number is False:
        return send_response(payload=not_found(), status=404)

    laws = random.sample(data, number)

    if bool(int(CACHE_ENABLED)):
        update_cache(laws)

    return show_laws(laws)


# Catch 404.
@app.errorhandler(404)
def page_not_found(e):
    return send_response(payload=not_found(), status=404)


def sigint(signal, frame):
    print(Fore.RED + "Server terminated." + Style.RESET_ALL)
    sys.exit(0)


signal.signal(signal.SIGINT, sigint)
