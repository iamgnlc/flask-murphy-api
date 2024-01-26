import json
import random
import signal
import sys
import os

from camel_converter import dict_to_camel
from colorama import Fore, Style
from flask import Flask, Response, request
from healthcheck import HealthCheck, EnvironmentDump
from threading import Thread

from app import AUTHOR, MAX_LAWS, SHOW_ENV_KEY, ENV
from app.utils import load_data, print_logo, validate
from app.utils import Cache, Message

app = Flask(__name__)

if ENV == "development":
    print_logo()

data = load_data()

default_headers = {
    "X-Author": AUTHOR,
    "X-Robots-Tag": "noindex",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS,PATCH,DELETE,POST,PUT",
    "Access-Control-Allow-Headers": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version",
}

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
    headers = {**default_headers, **custom_headers}

    payload = {**message.success(), **dict_to_camel(meta_data), "data": laws}

    return send_response(payload=payload, headers=headers)


def send_response(payload, status: int = 200, headers=default_headers):
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
    key = request.args.get("key")
    if key is None or key != SHOW_ENV_KEY:
        return send_response(
            payload=message.not_authorized(),
            status=message.not_authorized()["code"],
        )

    return environment_dump.run()


# Health check.
@app.route("/health")
def health():
    return health_check.run()


@app.route("/flush")
def flush():
    return send_response({**message.success(), "flush": cache.flush()})


# Show law(s).
@app.route("/")
@app.route("/<number>")
def main(number: int = 1):
    number = validate(number, 1, MAX_LAWS)

    if number is False:
        return send_response(
            payload=message.not_found(),
            status=message.not_found()["code"],
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
        payload=message.not_found(),
        status=message.not_found()["code"],
    )


def sigint(signal, frame):
    print(Fore.RED + "Server terminated." + Style.RESET_ALL)
    sys.exit(0)


signal.signal(signal.SIGINT, sigint)
