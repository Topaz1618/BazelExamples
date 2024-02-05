from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

    def get_client_ip(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        return remote_ip


class IndexHandler(BaseHandler):
    def get(self):
        # self.write("Hello World!")

        self.render("index.html")