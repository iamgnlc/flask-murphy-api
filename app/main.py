import random
import json

from flask import Flask, Response, abort, request
from app.utils.config import AUTHOR, MAX_LAWS
from app.utils.load_data import load_data
from app.utils.logo import logo
from app.utils.show_env import show_env, auth
from app.utils.validate import validate

app = Flask(__name__)

logo()

data = load_data()

def show_laws(laws):
    headers = {
        'X-Author': AUTHOR,
        'X-Count': len(laws),
        'X-Total-Count': len(data),
        'X-Robots-Tag': 'noindex',
    }
    response = Response(
        json.dumps(laws),
        mimetype='application/json',
        headers=headers
    )

    return response

# Show env vars only if authorized.
@app.route("/env")
def env():
    key = request.args.get('key')
    auth(key)

    return show_env()

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number, 1, MAX_LAWS)

    laws = random.sample(data, number)
    response = show_laws(laws)

    return response

# Catch all 404.
@app.route('/*')
def get():
    abort(404)
