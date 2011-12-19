#Small code to learn about Requesr Handlers

import tornado.web
import tornado.httpserver
import tornado.ioloop

from tornado.options import define, options

define("port", default=8888, help="run on given port", type=int)
define("mongodb_host",default="127.0.0.1:27017", help="blog database host")
define("mongodb_database",default="blog", help="blog database name")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("You requested the main page")

class BlogHandler(tornado.web.RequestHandler):
    def get(self, blog_id):
        self.write("You requested the blog " + blog_id)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/blog/([0-9]+)", BlogHandler),
])

def main():
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
