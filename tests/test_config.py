import os

from app import ENV


def test_env_defaults_to_development_when_not_on_vercel():
    # VERCEL_ENV is only set by the Vercel platform; locally it must default
    # to "development" so behavior is predictable outside production.
    vercel_env = os.getenv("VERCEL_ENV")
    if vercel_env:
        assert ENV == vercel_env
    else:
        assert ENV == "development"
