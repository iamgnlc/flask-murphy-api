from flask import Flask

import json
import random

app = Flask(__name__)

f = open('data.json')
data = json.load(f)

@app.route("/")
@app.route("/<number>")
def main(number = 1):
    number = int(number)

    if number > 10 or number < 0:
        number = 1

    law = random.sample(data, number)
    return law
