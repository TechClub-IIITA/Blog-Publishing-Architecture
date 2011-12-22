#Author: Divij Vaidya

import tornado.web
import tornado.httpserver
import tornado.ioloop
import re
from tornado.options import define, options
from mongoengine import *

define("port", default=64321, help="run on given port", type=int)
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
			(r"/feed",FeedHandler),
			(r"/entry/([^/]+)",EntryHandler)
		]
		connect('blog_database')


		setting=dict(
			xsrf_cookies=False,
			#login_url="auth/login",
			cookie_secret="AsdfsvAFDFavdaSVvfaA214eQEd324w2dF",
			blog_title="Tumblike",
			ui_modules={"Entry": EntryModule},
			autoescape=None
		)

		tornado.web.Application.__init__(self,handlers,**setting)

		
class User(Document):
        usrid=IntField()
        email = StringField(required=True)
	passwd = StringField(required=True)
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
		user_id=self.get_secure_cookie("user")
		if not user_id: 
			sef.write('cookie not verified')
			return
		return User.objects.get(usrid=user_id)
	def get_current_post_id(self):
		noOfPosts=len(Post.objects())
		return noOfPosts
	def get_current_user_id(self):
		noOfUsers=len(User.objects())
		return noOfUsers

class HomeHandler(BaseHandler):
	def get(self):
		#self.write('Inside HomeHandler')
		usr=self.get_current_user()
		
		entries=Post.objects(author=usr)
		if not entries:
			self.redirect("/compose")
			return 
		
		self.render("home.html", entries=entries)
		

class ComposeHandler(BaseHandler):
	def get(self):
		#usrid=self.get_argument("usrid",None);
		#To-Do: Check user authentication by a cookie here
		usrid=self.get_current_user().usrid
		entry=None;
		if not usrid:
			#The URL has been accessed directly
			raise tornado.web.HTTPError(403)
			return
		self.render("compose.html",entry=entry)
	def post(self):		
		#To-Do Expand to other posts than text post, expand to tags, expand to store date
		postcontent=self.get_argument("content")
		posttitle=self.get_argument("title")
		post = TextPost(title=posttitle, author=self.get_current_user())
		post.content = postcontent
		post.postid=self.get_current_post_id()+1;
		#post.tags = ['mongodb', 'mongoengine']
		post.save()

		self.redirect("/entry/"+str(post.postid))
		
	
class AboutHandler(BaseHandler):
	def get(self):
		self.render("about.html")

class FeedHandler(BaseHandler):
	def get(self):
		self.write("You have reached feed page")

class AuthLoginHandler(BaseHandler):
	def post(self):
		getemail=self.get_argument("email",None)
		pwd=self.get_argument("pwd",None)
		userlist=User.objects.get(email=getemail)
		dbpass=userlist.passwd
		
		if dbpass==pwd:
			#print('Login Sucessful')
			self.set_secure_cookie("user",str(userlist.usrid))
			#print('Cookie accepted')	
			self.redirect("/")
		else:
			raise tornado.web.HTTPError(500,"Invalid Email/Password")
		
		
class AuthLogoutHandler(BaseHandler):
	def get(self):
		self.write("You have reached logout page")
		self.clear_cookie("user")
		self.redirect("/index.html")

class EntryModule(tornado.web.UIModule):
	def render(self, entry):
		return self.render_string("entry.html", entry=entry)

class EntryHandler(BaseHandler):
	def get(self,path):
		entry1=Post.objects.get(postid=path)
		if not entry1:
			#No entry by this name
			raise tornado.web.HTTPError(404)
			return
		self.render("entry.html",entry=entry1)
			
def main():
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
