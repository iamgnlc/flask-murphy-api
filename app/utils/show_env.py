import os

from flask import abort
from app import SHOW_ENV_KEY
from app.utils.error import custom_error

def auth(key):
    if key is None or key != SHOW_ENV_KEY:
        return False
    
    return True

def show_env():
    response = {}
    for name, value in os.environ.items():
        response[name] = value

    return response
