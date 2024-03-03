from app.utils import default_headers


def test_default_headers():
    # it should return a dict.
    data = default_headers()
    assert isinstance(data, dict)
