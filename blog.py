#Small code to learn about Requesr Handlers

import tornado.web
import tornado.httpserver
import tornado.ioloop
import re
#import database
from tornado.options import define, options
from mongoengine import *

define("port", default=12346, help="run on given port", type=int)
define("mongodb_host",default="127.0.0.1:27017", help="blog database host")
define("mongodb_database",default="blog", help="blog database name")



class Application(tornado.web.Application):
	def __init__(self):
		handlers=[
			(r"/",HomeHandler),
			(r"/auth/login",AuthLoginHandler),
			(r"/auth/logout",AuthLogoutHandler),
			(r"/compose",ComposeHandler),
			(r"/about",AboutHandler),
			(r"/feed",FeedHandler)
		]

		setting=dict(
			xsrf_cookies=True,
			login_url="auth/login",
			cookie_secret="AsdfsvAFDFavdaSVvfaA214eQEd324w2dF",
		)

		tornado.web.Application.__init__(self,handlers,**setting)

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
	postid=IntField()
        title = StringField(max_length=120, required=True)
        author = ReferenceField(User, reverse_delete_rule=CASCADE)
        tags = ListField(StringField(max_length=30))
        comments = ListField(EmbeddedDocumentField(Comment))
	date=DateTimeField()

class TextPost(Post):
        content = StringField()

class ImagePost(Post):
        image_path = StringField()

class LinkPost(Post):
        link_url = StringField()

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		#user_id=self.get_secure_cookie("user")
		user_id=1000
		if not user_id: return None
		return User.objects(usrid=user_id)

class HomeHandler(BaseHandler):
	def get(self):
		self.write('Inside HomeHandler')
		usr=self.get_current_user()
		if len(usr)>1:
			self.write("More than one person logged in ")
			return None
		
		for authobj in usr:
			entries=Post.objects(author=authobj)
		if not entries:
			self.redirect("/compose")
		return 
		self.render("home.html", entries=entries)

class ComposeHandler(BaseHandler):
	def get(self):
		pstid=self.get_argument("id",None);
		entry=None;
		if pstid:
			#if a post already exists by the same ID
			entry=Post.objects(postid=pstid)
		self.render("compose.html",entry=entry)
	
class AboutHandler(BaseHandler):
	def get(self):
		self.render("about.html")

class FeedHandler(BaseHandler):
	def get(self):
		self.write("You have reached feed page")
class AuthLoginHandler():
	def get(self):
		self.write("You have reached login page")
class AuthLogoutHandler():
	def get(self):
		self.write("You have rached logout page")
		
def main():
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
