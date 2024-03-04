from app import AUTHOR


allowed_methods = ["GET", "OPTIONS", "PATCH", "DELETE", "POST", "PUT"]

allowed_headers = [
    "X-CSRF-Token",
    "X-Requested-With",
    "Accept",
    "Accept-Version",
    "Content-Length",
    "Content-MD5",
    "Content-Type",
    "Date",
    "X-Api-Version",
]


def default_headers():
    return {
        "X-Author": AUTHOR,
        "X-Robots-Tag": "noindex",
        # CORS.
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": ",".join(map(str, allowed_methods)),
        "Access-Control-Allow-Headers": ",".join(map(str, allowed_headers)),
    }
