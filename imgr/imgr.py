# -*- coding: utf-8 -*-
import tornado.ioloop
from tornado.web import Application, RequestHandler
from tornado.options import define, options
import time
from tasks import add

class MainHandler(RequestHandler):

    def get(self):
        self.write('Hello, world!')


def my_callback():
    import random
    a = random.randint(0,10)
    b = random.randint(0,10)
    add.delay(a, b)


def main():
    define("host", default="127.0.0.1", help="Host IP")
    define("port", default=8080, help="Port")
    tornado.options.parse_command_line()

    application = Application([(r"/", MainHandler),])

    application.listen(options.port, options.host)

    periodic = tornado.ioloop.PeriodicCallback(my_callback, 10000)
    periodic.start()

    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
