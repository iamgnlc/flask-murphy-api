import random
import os

from flask import Flask, Response,send_from_directory
from utils.config import *
from utils.load_data import *
from utils.logo import *

app = Flask(__name__)

logo()

def validate(number):
    number = int(number)

    if number > MAX_LAWS:
        number = MAX_LAWS

    if number < 1:
        number = 1

    return number

def set_response(laws):
    response = Response(json.dumps(laws), mimetype='application/json')
    response.headers['X-Author'] = AUTHOR
    response.headers['X-Count'] = len(laws)
    response.headers['X-Total-Count'] = len(data)
    response.headers['X-Robots-Tag'] = 'noindex'

    return response

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number)

    laws = random.sample(data, number)
    response = set_response(laws)

    return response