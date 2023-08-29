import json


def load_data():
    file = open("db/data.json")
    data = json.load(file)

    return data
