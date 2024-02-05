import os.path
import asyncio
import multiprocessing

import tornado.httpserver
import tornado.web
import tornado.options
from tornado.options import define, options


from file_management import IndexHandler


define("port", default=8011, help="run on the given port", type=int)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "default_locale": "en_US.UTF-8",
        "default_encoding": "utf-8",
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "login_url": "/login",
    }

    application = tornado.web.Application([
        (r"/static/", tornado.web.StaticFileHandler, {"path": settings["static_path"]}),

        (r'/', IndexHandler),

    ], debug=True, **settings)

    try:
        loop = asyncio.get_event_loop()

        # Create an HTTP server instance
        http_server = tornado.httpserver.HTTPServer(
            application,
            # ssl_options=context,
            max_buffer_size=10485760000)

        # Listen on the specified port
        http_server.listen(options.port)
        print("server start")

        # Start the event loop
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt as e:
        print("Quit")
