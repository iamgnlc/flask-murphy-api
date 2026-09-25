from unittest.mock import patch

import pytest
import redis

from app import DEFAULT_LOCALE
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


def test_get_root_returns_default_locale(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["locale"] == DEFAULT_LOCALE
    assert response.headers["X-Locale"] == DEFAULT_LOCALE
    assert all("Tutto" not in law["law"] for law in data["data"])


def test_get_count_route_returns_default_locale(client):
    response = client.get("/5")
    assert response.status_code == 200
    data = response.get_json()
    assert data["locale"] == DEFAULT_LOCALE
    assert data["returnCount"] == 5


def test_get_locale_returns_one_law(client):
    response = client.get("/en")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 200
    assert data["locale"] == "en"
    assert data["returnCount"] == 1
    assert len(data["data"]) == 1
    assert response.headers["X-Locale"] == "en"


def test_get_locale_with_count(client):
    response = client.get("/it/2")
    assert response.status_code == 200
    data = response.get_json()
    assert data["locale"] == "it"
    assert data["returnCount"] == 2
    assert len(data["data"]) == 2
    assert response.headers["X-Locale"] == "it"


def test_get_unknown_locale_with_count_returns_404(client):
    response = client.get("/xx/2")
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == 404
    assert data["status"] == "not found"


def test_get_locale_with_invalid_count_returns_400(client):
    response = client.get("/it/abc")
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == 400
    assert data["status"] == "bad request"


def test_get_locale_clamps_over_max(client):
    response = client.get("/it/999")
    assert response.status_code == 200
    data = response.get_json()
    assert data["locale"] == "it"
    assert data["returnCount"] == 50


def test_get_unknown_single_segment_returns_404(client):
    # /foo matches /<number> but identifies no resource: 404, not 400.
    for path in ("/foo", "/notanumber", "/foo/"):
        response = client.get(path)
        assert response.status_code == 404
        data = response.get_json()
        assert data["code"] == 404
        assert data["status"] == "not found"


def test_trailing_slash_is_accepted_on_all_routes(client):
    # strict_slashes is disabled: /it/ == /it, /5/ == /5, etc.
    response = client.get("/it/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["locale"] == "it"
    assert data["returnCount"] == 1

    for path in ("/5/", "/en/3/", "/it/2/", "/health/"):
        response = client.get(path)
        assert response.status_code == 200, path

    response = client.get("/xx/2/")
    assert response.status_code == 404


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


def test_get_flush_redis_down_returns_200(client):
    # /flush is best-effort: an unreachable Redis must not produce a 500.
    class ExplodingCache:
        @property
        def flush(self):
            raise redis.ConnectionError("Redis down")

    with patch("app.main.cache", new=ExplodingCache()):
        response = client.get("/flush")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 200
    assert data["status"] == "success"
    assert data["flush"] is False


def test_get_nonexistent_route_returns_404(client):
    response = client.get("/some/nonexistent/path")
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == 404
    assert data["status"] == "not found"


def test_rate_limit_returns_429(client):
    with patch("app.main.limiter"), app.test_request_context():
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
