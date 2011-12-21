#Small code to learn about Requesr Handlers

import tornado.web
import tornado.httpserver
import tornado.ioloop
import re
import database
from tornado.options import define, options
from mongoengine import *

define("port", default=8888, help="run on given port", type=int)
define("mongodb_host",default="127.0.0.1:27017", help="blog database host")
define("mongodb_database",default="blog", help="blog database name")



class Application(tornado.web.Application):
	def __init__(self):
		handlers=[
			(r"/",HomeHandler),
	#		(r"/auth/login",AuthHandler),
	#		(r"/auth/logout",AuthHandler),
			(r"/compose",ComposeHandler)
		]

		tornado.web.Application.__init__(self,handlers)

		connect('blog_database')


class User(Document):
        usrid=IntField()
        email = StringField(required=True)
        first_name = StringField(max_length=50)
        last_name = StringField(max_length=50)

class Comment(EmbeddedDocument):
        content = StringField()
        name = StringField(max_length=120)

class Post(Document):
        title = StringField(max_length=120, required=True)
        author = ReferenceField(User, reverse_delete_rule=CASCADE)
        tags = ListField(StringField(max_length=30))
        comments = ListField(EmbeddedDocumentField(Comment))

class TextPost(Post):
        content = StringField()

class ImagePost(Post):
        image_path = StringField()

class LinkPost(Post):
        link_url = StringField()

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		#user_id=self.get_secure_cookie("user")
		self.write("Returning user ID 1000")
		user_id=1000
		if not user_id: return None
		return User.objects(id=user_id)

class HomeHandler(BaseHandler):
	def get(self):
		self.write('Inside HomeHandler')
		#entries=Post.objects(author=self.get_current_user())
		#if not entries:
		#	self.redirect("/compose")
		#return 
#		self.render("home.html", entries=entries)

class ComposeHandler(BaseHandler):
	def get(self):
		self.write("You have reached compose page")
def main():
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
