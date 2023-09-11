from app.utils import Error

error = Error()


def test_not_found():
    # it should return 404.
    response = error.not_found()
    assert response["code"] == 404


def test_not_authorized():
    # it should return 403.
    response = error.not_authorized()
    assert response["code"] == 403
