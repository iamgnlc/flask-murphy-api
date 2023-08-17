import random
import json

from flask import Flask, Response, request
from app import AUTHOR, MAX_LAWS, SHOW_ENV_KEY
from app.utils import load_data, print_logo, show_env, validate

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

def error_message(code, message):
    return {'code': code, 'message': message}

# Show env vars only if authorized.
@app.route("/env")
def env():
    key = request.args.get('key')
    if key is None or key != SHOW_ENV_KEY:
        error_code = 403
        return error_message(error_code, 'Not Authorized'), error_code

    return show_env()

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number, 1, MAX_LAWS)

    if number is False:
        error_code = 404
        return error_message(error_code, 'Not Found'), error_code

    laws = random.sample(data, number)
    response = show_laws(laws)

    return response

# Catch 404.
@app.errorhandler(404)
def page_not_found(e):
    error_code = 404
    return error_message(error_code, 'Not Found'), error_code
