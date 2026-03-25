import pytest
from unittest.mock import patch

from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_root_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 200
    assert data["status"] == "success"
    assert data["returnCount"] == 1
    assert len(data["data"]) == 1


def test_get_multiple_laws(client):
    response = client.get("/5")
    assert response.status_code == 200
    data = response.get_json()
    assert data["returnCount"] == 5
    assert len(data["data"]) == 5


def test_get_invalid_input_returns_400(client):
    response = client.get("/notanumber")
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == 400
    assert data["status"] == "bad request"


def test_get_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_get_env_without_key_returns_403(client):
    response = client.get("/env")
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == 403


def test_get_env_with_valid_key(client):
    from app import SHOW_ENV_KEY

    response = client.get(f"/env?key={SHOW_ENV_KEY}")
    if SHOW_ENV_KEY and SHOW_ENV_KEY != "":
        assert response.status_code == 200
        data = response.get_json()
        assert data["code"] == 200
        assert "data" in data
    else:
        assert response.status_code == 403


def test_get_flush(client):
    with patch("app.main.cache") as mock_cache:
        mock_cache.flush = True
        response = client.get("/flush")
        assert response.status_code == 200
        data = response.get_json()
        assert data["code"] == 200
        assert "flush" in data


def test_get_nonexistent_route_returns_404(client):
    response = client.get("/some/nonexistent/path")
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == 404
    assert data["status"] == "not found"


def test_rate_limit_returns_429(client):
    with patch("app.main.limiter"):
        # Trigger 429 directly via the error handler
        with app.test_request_context():
            from app.main import too_many_requests
            response = too_many_requests(None)
            data = response.get_json()
            assert data["code"] == 429
            assert data["status"] == "too many requests"


def test_get_over_max_clamps(client):
    response = client.get("/999")
    assert response.status_code == 200
    data = response.get_json()
    assert data["returnCount"] == 50


def test_response_has_custom_headers(client):
    response = client.get("/")
    assert "X-Count" in response.headers
    assert "X-Total-Count" in response.headers
    assert "X-Author" in response.headers


def test_sigint_handler():
    from app.main import sigint
    with pytest.raises(SystemExit) as exc_info:
        sigint(None, None)
    assert exc_info.value.code == 0
