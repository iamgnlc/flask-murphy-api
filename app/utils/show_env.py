import os

from flask import abort
from utils.config import SHOW_ENV_KEY

def auth(key):
    if key is None or key != SHOW_ENV_KEY:
        abort(404)

def show_env():
    response = {}
    for name, value in os.environ.items():
        response[name] = value

    return response
