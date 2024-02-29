import json


def load_data():
    file = open("db/data.json")
    data = tuple(json.load(file))

    return data
