import json
import os


def load_data():
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "db",
        "data.json",
    )
    with open(data_path) as file:
        data = tuple(json.load(file))

    return data
