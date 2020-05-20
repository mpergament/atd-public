#!/usr/bin/python3
import tornado.ioloop
import asyncio
import os

# Import frontend and backend files
from Web.backend import BackEnd
from Web.frontend import FrontEnd

def create_app():
    return tornado.web.Application([
        (r"/labs/",FrontEnd),
        (r"/backend/",BackEnd)],
        static_path=os.getcwd())


if __name__ == '__main__':
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # Testing Only
    app = create_app()
    app.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()