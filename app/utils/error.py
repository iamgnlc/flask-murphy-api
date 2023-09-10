def error_message(code: int, message: str):
    return {"code": code, "message": message}


def not_found():
    code = 404
    message = "Not Found"
    return error_message(code, message)


def not_authorized():
    code = 403
    message = "Not Authorized"
    return error_message(code, message)
