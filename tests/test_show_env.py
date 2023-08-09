from utils.show_env import show_env

def test_show_env():
    # it should show env as json
    env = show_env()
    assert type(env) is dict
