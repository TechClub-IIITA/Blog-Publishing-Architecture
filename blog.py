#Author: Divij Vaidya

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.auth
import re
import datetime
import tornado.options
import os.path
from tornado.options import define, options
from mongoengine import *

define("port", default=8888, help="run on given port", type=int)

define("mongodb_host",default="127.0.0.1:27017", help="blog database host")#Not bring used right now
define("mongodb_database",default="blog", help="blog database name")#Not being used right now
define("facebook_app_id", default="346477282033995", help="Facebook Application ID")
define("facebook_app_secret", default="22a4bc18c6a6579f08cb485480b7f064", help="Facebook Application Secret")


class Application(tornado.web.Application):
	def __init__(self):
		handlers=[
			(r"/",HomeHandler),
			(r"/auth/login",AuthLoginHandler),
			(r"/auth/logout",AuthLogoutHandler),
			(r"/compose",ComposeHandler),
			(r"/about",AboutHandler),
			(r"/feed",FeedHandler),#To-Do
			(r"/entry/([^/]+)",EntryHandler),
			(r"/register",RegisterHandler),
			(r"/auth/login/fb",FacebookGraphLoginHandler)
		]
		connect('blog_database')


		setting=dict(
			xsrf_cookies=False,
			login_url="auth/login",
			cookie_secret="AsdfsvAFDFavdaSVvfaA214eQEd324w2dF",
			blog_title="Tumblike",
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			ui_modules={"Entry": EntryModule},
			autoescape=None,
			facebook_secret=options.facebook_app_secret,
			facebook_api_key=options.facebook_app_id
		)

		tornado.web.Application.__init__(self,handlers,**setting)

		
class User(Document):
        usrid=IntField()
        email = StringField()
	passwd = StringField()
        first_name = StringField(max_length=50)
        last_name = StringField(max_length=50)
	usrtype=IntField() #0 for normal 1 for facebook

class Comment(EmbeddedDocument):
        content = StringField()
        name = StringField(max_length=120,required=True)
	date=DateTimeField(default=datetime.datetime.now())

class Post(Document):
	postid=IntField()
        title = StringField(max_length=120, required=True)
        author = ReferenceField(User, reverse_delete_rule=CASCADE)
        tags = ListField(StringField(max_length=30))
        comments = ListField(EmbeddedDocumentField(Comment))
	date=DateTimeField(default=datetime.datetime.now())

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
			#self.write('cookie not verified')
			print "Cookie Verification Filed"
			#self.render("index.html")
			return None
		return User.objects.get(usrid=user_id)
	
	def get_current_post_id(self):
		noOfPosts=len(Post.objects())
		return noOfPosts
	def get_current_user_id(self):
		noOfUsers=len(User.objects())
		return noOfUsers

class HomeHandler(BaseHandler):
	def get(self):
		usr=self.get_current_user()
		if not usr:
			self.render("index.html")
			return
		
		entries=Post.objects(author=usr).order_by("-date")
		if not entries:
			self.redirect("/compose")
			return 
		
		self.render("home.html", entries=entries)
		

class ComposeHandler(BaseHandler):
	def get(self):
		usridobj=self.get_current_user();
		entry=None;
		if not usridobj:
			#The URL has been accessed directly
			raise tornado.web.HTTPError(404,"Forbidden Access")
			return
		self.render("compose.html",entry=entry)
	def post(self):		
		#To-Do Expand to other posts than text post, expand to tags, expand to store date
		postcontent=self.get_argument("post-content")
		posttitle=self.get_argument("post-title")
		tags=self.get_argument("tags")
		post = TextPost(title=posttitle, author=self.get_current_user())
		post.content = postcontent
		post.postid=self.get_current_post_id()+1
		post.tags = tags.split(',')
		post.date=datetime.datetime.now()
		post.save()

		self.redirect("/entry/"+str(post.postid))
		
	
class AboutHandler(BaseHandler):
	def get(self):
		self.render("about.html")

class FeedHandler(BaseHandler):
	def get(self):
		self.write("You have reached feed page")

class AuthLoginHandler(BaseHandler):
	def get(self):
		self.render("index.html")
	def post(self):
		getemail=self.get_argument("email",None)
		pwd=self.get_argument("password",None)
		userlist=User.objects.get(email=getemail)
		if usrtype==1:
			raise tornado.web.HTTPError(500,"Facebook Login Required")
			return
		dbpass=userlist.passwd
	
		if dbpass==pwd:
			self.set_secure_cookie("user",str(userlist.usrid))
			self.redirect("/")
		else:
			raise tornado.web.HTTPError(500,"Invalid Email/Password")

		
		
class AuthLogoutHandler(BaseHandler):
	def get(self):
		self.write("You have successfully logged out")
		self.clear_cookie("user")
		

class EntryModule(tornado.web.UIModule):
	def render(self, entry):
		return self.render_string("entry.html", entry=entry,show_comments=False,entry_page=False)

class EntryHandler(BaseHandler):
#	@tornado.web.asynchronous
	def get(self,path):
		entry1=Post.objects.get(postid=path)
		if not entry1:
			#No entry by this name
			raise tornado.web.HTTPError(404)
			return
		self.render("entry.html",entry=entry1,show_comments=True,entry_page=True)
		return
	def post(self,path):
		newcomment=self.get_argument("comment")
		commentusrname=self.get_argument("name")
		entry=Post.objects.get(postid=path)
		com=Comment(name=commentusrname,content=newcomment)
		com.date=datetime.datetime.now()
		entry.comments.append(com)
		entry.save()
                self.render("entry.html",entry=entry,show_comments=True,entry_page=True)
		return
class RegisterHandler(BaseHandler):
	def get(self):
		self.render("register.html")
		return
	def post(self):
		newuser_first_name=self.get_argument("first")
		newuser_last_name=self.get_argument("last")
		newuser_email=self.get_argument("email")
		newuser_pwd=self.get_argument("pass")

		if ((not newuser_email) or ( not newuser_pwd)):
			self.redirect("/register")
			return
		newuser_usrid=self.get_current_user_id()+1
		nuusr=User(usrid=newuser_usrid,email=newuser_email,passwd=newuser_pwd,first_name=newuser_first_name,last_name=newuser_last_name,usrtype=0)
		nuusr.save()
		self.redirect("/")
class FacebookGraphLoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
	@tornado.web.asynchronous
	def get(self):
		if self.get_argument("code", False):
			self.get_authenticated_user(redirect_uri='http://localhost:8888/auth/login/fb',client_id=self.settings["facebook_api_key"],client_secret=self.settings["facebook_secret"],code=self.get_argument("code"),callback=self.async_callback(self._on_login))
			return
		
		self.authorize_redirect(redirect_uri='http://localhost:8888/auth/login/fb',client_id=self.settings["facebook_api_key"],extra_params={"scope": "read_stream,offline_access"})

	def _on_login(self, user):
		if not user:
			raise tornado.web.HTTPError(500,"Facebook Authentication Failed")
		
		chkusr=User.objects.get(usrtype=1,first_name=user["first_name"],last_name=user["last_name"])
		usrid=None
		
		if not chkusr:
			newuser_first_name=user["first_name"]
	                newuser_last_name=user["last_name"]
        	        newuser_email=None
                	newuser_pwd=None
	                newuser_usrid=self.get_current_user_id()+1
        	        nuusr=User(usrid=newuser_usrid,email=newuser_email,passwd=newuser_pwd,first_name=newuser_first_name,last_name=newuser_last_name,usrtype=1)
                	nuusr.save()
			usrid=newuser_usrid
		usrid=chkusr.usrid	
		self.set_secure_cookie("user",str(usrid))
		self.redirect("/")
			
def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
