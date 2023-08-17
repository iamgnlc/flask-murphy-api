import os

def show_env():
    response = {}
    for name, value in os.environ.items():
        response[name] = value

    return response