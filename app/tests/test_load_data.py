from utils.load_data import data

def test_load_data():
    # it should load data from json
    assert type(data) is list
