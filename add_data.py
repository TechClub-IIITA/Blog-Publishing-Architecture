from mongoengine import *

connect('blog_database')

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



#post1 = TextPost(title='Fun with MongoEngine v2.0', author=User.objects.get(email="john@example.com"))
#post1.content = 'I took a look at MongoEngine today, looks pretty cool.'
#post1.tags = ['mongodb', 'mongoengine']
#post1.save()
post1=Post.objects()
post1.delete()

