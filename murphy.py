import json
import random

from flask import Flask, Response
from utils.config import *

MAX_LAWS = 50

app = Flask(__name__)

file = open('data.json')
data = json.load(file)

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

    return response

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number)

    laws = random.sample(data, number)
    response = set_response(laws)

    return response