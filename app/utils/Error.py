class Error:
    def not_found(self):
        code = 404
        message = "Not Found"
        return self._error_message(code, message)

    def not_authorized(self):
        code = 403
        message = "Not Authorized"
        return self._error_message(code, message)

    def _error_message(self, code, message):
        return {"code": code, "message": message}
