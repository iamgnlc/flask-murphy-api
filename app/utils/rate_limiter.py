from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def rate_limiter(app):
    return Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["50000 per day", "90 per minute"],
        storage_uri="memory://",
    )
