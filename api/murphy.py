from flask import Flask, Response

import json
import random

from dotenv import load_dotenv
load_dotenv()

import os

AUTHOR = os.getenv("AUTHOR")

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

    return response

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number)

    # print (len(data))

    laws = random.sample(data, number)
    response = set_response(laws)

    return response