from waitress import serve
from app import main
import sys

HOST = "127.0.0.1"
PORT = 8080

if len(sys.argv) == 2:
    PORT = sys.argv[1]

serve(main.app, host=HOST, port=PORT)
