import random
import os

from flask import Flask, Response,send_from_directory
from utils.config import *
from utils.load_data import *
from utils.logo import logo
from utils.show_env import show_env

app = Flask(__name__)

logo()

def validate(number):
    number = int(number)

    if number > MAX_LAWS:
        number = MAX_LAWS

    if number < 1:
        number = 1

    return number

def show_laws(laws):
    response = Response(json.dumps(laws), mimetype='application/json')
    response.headers['X-Author'] = AUTHOR
    response.headers['X-Count'] = len(laws)
    response.headers['X-Total-Count'] = len(data)
    response.headers['X-Robots-Tag'] = 'noindex'

    return response

@app.route("/env")
def env():
    return show_env()

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number)

    laws = random.sample(data, number)
    response = show_laws(laws)

    return response