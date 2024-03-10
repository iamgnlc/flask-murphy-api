from app.utils import Message

message = Message()


def test_success():
    # it should return 200.
    response = message.success
    assert response["code"] == 200


def test_not_found():
    # it should return 404.
    response = message.not_found
    assert response["code"] == 404


def test_not_authorized():
    # it should return 403.
    response = message.not_authorized
    assert response["code"] == 403


def test_too_many_requests():
    # it should return 403.
    response = message.too_many_requests
    assert response["code"] == 429
