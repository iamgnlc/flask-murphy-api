from app.utils import show_env


def test_show_env():
    # it should show env as json.
    env = show_env()
    assert isinstance(env, dict)
    assert len(env) > 0
