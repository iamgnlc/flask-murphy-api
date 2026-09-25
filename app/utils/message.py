class Message:
    @property
    def success(self):
        return {"code": 200, "status": "success"}

    @property
    def not_found(self):
        return {"code": 404, "status": "not found"}

    @property
    def not_authorized(self):
        return {"code": 403, "status": "not authorized"}

    @property
    def too_many_requests(self):
        return {"code": 429, "status": "too many requests"}

    @property
    def bad_request(self):
        return {"code": 400, "status": "bad request"}
