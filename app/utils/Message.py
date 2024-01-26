class Message:
    def success(self):
        self.code = 200
        self.status = "success"
        return self.__send_message()

    def not_found(self):
        self.code = 404
        self.status = "not found"
        return self.__send_message()

    def not_authorized(self):
        self.code = 403
        self.status = "not authorized"
        return self.__send_message()

    def __send_message(self):
        return {"code": self.code, "status": self.status}
