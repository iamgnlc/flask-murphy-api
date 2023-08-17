import random
import json

from flask import Flask, Response, request
from app import AUTHOR, MAX_LAWS, SHOW_ENV_KEY
from app.utils import load_data, print_logo, show_env, validate
from app.utils import not_found, not_authorized

app = Flask(__name__)

print_logo()

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
    if key is None or key != SHOW_ENV_KEY:
        return not_authorized()

    return show_env()

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number, 1, MAX_LAWS)

    if number is False:
        return not_found()

    laws = random.sample(data, number)
    response = show_laws(laws)

    return response

# Catch 404.
@app.errorhandler(404)
def page_not_found(e):
    return not_found()
