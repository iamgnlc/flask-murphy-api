from app.utils import load_data

def test_load_data():
    # it should load data from json
    data = load_data()
    assert type(data) is list
