from app.utils import Message

message = Message()


def test_not_found():
    # it should return 404.
    response = message.not_found()
    assert response["code"] == 404


def test_not_authorized():
    # it should return 403.
    response = message.not_authorized()
    assert response["code"] == 403
