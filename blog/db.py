from flask import g
from pymongo import MongoClient
from mongoengine import *
from werkzeug.security import generate_password_hash
import datetime


# def get_db():
#     """Connect to the application's configured database. The connection
#     is unique for each request and will be reused if this is called
#     again.
#     """
#     client = MongoClient('localhost', 27017)
#     if "db" not in g:
#         g.db = client.blog
#     return g.db
#

connect('blog')


class User(Document):
    username = StringField(required=True)
    password = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    email = StringField(max_length=60)
    address = StringField(max_length=250)
    instagram = StringField(max_length=50)
    telegram = StringField(max_length=50)
    followings = ListField(StringField(max_length=50))
    followers = ListField(StringField(max_length=50))


def create_user(username, password, first_name, last_name, email, address=None, instagram=None, telegram=None):
    try:
        new_user = User()
        new_user.username = username
        new_user.password = generate_password_hash(password, "sha256")
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.email = email
        new_user.address = address
        new_user.instagram = instagram
        new_user.telegram = telegram
        new_user.save()
        return new_user
    except:
        return False


class Category(Document):
    title = StringField(max_length=50)
    description = StringField(max_length=250)
    child = ListField(ReferenceField('self'))
    parent = ReferenceField('self')


class Comment(EmbeddedDocument):
    user = ReferenceField(User)
    text = StringField(max_length=250)
    time = DateTimeField(default=datetime.datetime.utcnow)


class Post(Document):
    title = StringField(max_length=150)
    body = StringField(max_length=1200)
    user = ReferenceField(User)
    category = ReferenceField(Category)
    main_image = StringField(max_length=150)
    images = ListField(StringField(max_length=150))
    likes = ListField(User)
    dislike = ListField(User)
    time = DateTimeField(default=datetime.datetime.utcnow)
    comment = ListField(EmbeddedDocumentField(Comment))
    draft = BooleanField()
