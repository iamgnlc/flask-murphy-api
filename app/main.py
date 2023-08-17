import random
import json

from flask import Flask, Response, request
from app import AUTHOR, MAX_LAWS
from app.utils.load_data import load_data
from app.utils.logo import logo
from app.utils.show_env import show_env, auth
from app.utils.validate import validate
from app.utils.error import custom_error

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
    is_auth = auth(key)

    if is_auth:
        return show_env()
    else:
        error_code = 403
        return custom_error({'status': error_code, 'message': 'Not Authorized'}, error_code)

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number, 1, MAX_LAWS)

    laws = random.sample(data, number)
    response = show_laws(laws)

    return response

# Catch 404.
@app.errorhandler(404)
def page_not_found(e):
    return custom_error({'status': e.code, 'message': str(e.description)}, e.code)
