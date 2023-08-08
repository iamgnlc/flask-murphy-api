import random
import os

from flask import Flask, Response, abort
from utils.config import *
from utils.load_data import *
from utils.logo import logo
from utils.show_env import show_env
from utils.validate import validate

app = Flask(__name__)

logo()

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

@app.route("/env")
def env():
    return show_env()

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number, 1, MAX_LAWS)

    laws = random.sample(data, number)
    response = show_laws(laws)

    return response

@app.route('/*')
def get():
    abort(404)
