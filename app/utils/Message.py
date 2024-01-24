class Message:
    code = 200
    status = "success"

    def success(self):
        return self.__error_message()

    def not_found(self):
        self.code = 404
        self.status = "not found"
        return self.__error_message()

    def not_authorized(self):
        self.code = 403
        self.status = "not authorized"
        return self.__error_message()

    def __error_message(self):
        return {"code": self.code, "status": self.status}
