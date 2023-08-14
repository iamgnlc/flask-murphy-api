from waitress import serve
from app import main

HOST='127.0.0.1'
PORT=8080

serve(main.app, host=HOST, port=PORT)