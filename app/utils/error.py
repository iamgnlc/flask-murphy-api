def error_message(code, message):
    return {'code': code, 'message': str(message)}

def not_found():
    code = 404
    message = 'Not Found'
    return error_message(code, message), code

def not_authorized():
    code = 403
    message = 'Not Authorized'
    return error_message(code, message), code
