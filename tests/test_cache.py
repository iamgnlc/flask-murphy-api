import time
from unittest.mock import patch, MagicMock

import redis

from app.utils.Cache import Cache


@patch("app.utils.Cache.redis.Redis")
def test_ping_success(mock_redis_cls):
    mock_conn = MagicMock()
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    assert cache.ping is True
    mock_conn.ping.assert_called_once()


@patch("app.utils.Cache.redis.Redis")
def test_ping_failure(mock_redis_cls):
    mock_conn = MagicMock()
    mock_conn.ping.side_effect = redis.ConnectionError("Connection refused")
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    assert cache.ping is False


@patch("app.utils.Cache.redis.Redis")
def test_ping_memoized(mock_redis_cls):
    mock_conn = MagicMock()
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    # First call hits Redis
    assert cache.ping is True
    # Second call within TTL uses cached result
    assert cache.ping is True
    # Only one actual Redis ping call
    mock_conn.ping.assert_called_once()


@patch("app.utils.Cache.redis.Redis")
def test_ping_refreshes_after_ttl(mock_redis_cls):
    mock_conn = MagicMock()
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    assert cache.ping is True
    # Force TTL expiry
    cache._ping_checked_at = time.monotonic() - 10
    assert cache.ping is True
    assert mock_conn.ping.call_count == 2


@patch("app.utils.Cache.redis.Redis")
def test_flush(mock_redis_cls):
    mock_conn = MagicMock()
    mock_conn.flushall.return_value = True
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    assert cache.flush is True
    mock_conn.flushall.assert_called_once()


@patch("app.utils.Cache.redis.Redis")
def test_update_with_laws(mock_redis_cls):
    mock_conn = MagicMock()
    mock_pipe = MagicMock()
    mock_conn.pipeline.return_value = mock_pipe
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    laws = [{"law": "Anything that can go wrong will go wrong."}]
    cache.update(laws)
    mock_pipe.set.assert_called_once()
    mock_pipe.execute.assert_called_once()


@patch("app.utils.Cache.redis.Redis")
def test_update_empty_laws(mock_redis_cls):
    mock_conn = MagicMock()
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    cache.update([])
    mock_conn.pipeline.assert_not_called()


@patch("app.utils.Cache.redis.Redis")
def test_update_connection_error(mock_redis_cls):
    mock_conn = MagicMock()
    mock_pipe = MagicMock()
    mock_pipe.execute.side_effect = redis.ConnectionError("Connection lost")
    mock_conn.pipeline.return_value = mock_pipe
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    # Should not raise, just log
    cache.update([{"law": "Test law"}])
    mock_pipe.execute.assert_called_once()


@patch("app.utils.Cache.redis.Redis")
def test_content_based_keys_are_deterministic(mock_redis_cls):
    mock_conn = MagicMock()
    mock_pipe = MagicMock()
    mock_conn.pipeline.return_value = mock_pipe
    mock_redis_cls.return_value = mock_conn
    cache = Cache()
    law = {"law": "Test law"}
    cache.update([law])
    first_key = mock_pipe.set.call_args_list[0][0][0]
    mock_pipe.reset_mock()
    cache.update([law])
    second_key = mock_pipe.set.call_args_list[0][0][0]
    assert first_key == second_key
    assert first_key.startswith("murphy:")
