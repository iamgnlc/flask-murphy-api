from utils.validate import validate

def test_max():
    # it should return max number allowed
    number = validate(15, 1, 10)
    assert number == 10

def test_min():
    # it should return min number allowed
    number = validate(-1, 1, 10)
    assert number == 1
