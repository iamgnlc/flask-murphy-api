from app.utils import not_found, not_authorized

def test_not_found():
    # it should return 404.
    response = not_found()
    assert response[0]['code'] == 404

def test_not_authorized():
    # it should return 403.
    response = not_authorized()
    assert response[0]['code'] == 403
