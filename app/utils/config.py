import os

from dotenv import load_dotenv
load_dotenv()

AUTHOR = os.getenv("AUTHOR")
SHOW_ENV_KEY = os.getenv("SHOW_ENV_KEY")

MAX_LAWS = 50
