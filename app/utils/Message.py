class Message:
    def ok(self):
        code = 200
        status = "success"
        return self._error_message(code, status)

    def not_found(self):
        code = 404
        status = "not found"
        return self._error_message(code, status)

    def not_authorized(self):
        code = 403
        status = "not authorized"
        return self._error_message(code, status)

    def _error_message(self, code, status):
        return {"code": code, "status": status}
