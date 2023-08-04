from flask import Flask

import json
import random

app = Flask(__name__)

file = open('data.json')
data = json.load(file)

def validate(number):
    number = int(number)

    if number > 10:
        number = 10

    if number < 1:
        number = 1

    return number

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = validate(number)

    law = random.sample(data, number)
    return law
