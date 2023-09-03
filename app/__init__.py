import os

from dotenv import load_dotenv

load_dotenv()

AUTHOR = os.getenv("AUTHOR")
SHOW_ENV_KEY = os.getenv("SHOW_ENV_KEY")
CACHE_HOST = os.getenv("CACHE_HOST")
CACHE_PASSWORD = os.getenv("CACHE_PASSWORD")
CACHE_PORT = os.getenv("CACHE_PORT")
CACHE_TTL = os.getenv("CACHE_TTL")

MAX_LAWS = 50
