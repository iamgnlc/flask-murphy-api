from dotenv import load_dotenv
load_dotenv()

import os

AUTHOR = os.getenv("AUTHOR")

MAX_LAWS = 50