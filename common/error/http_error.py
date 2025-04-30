class HTTPError(Exception):
    def __init__(self, *, content, status):
        self.content = content
        self.status = status
        super().__init__(str({"status": status, "content": content}))
