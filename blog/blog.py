import functools
import os
from os.path import join, dirname, realpath

import mongoengine
from bson import ObjectId, BSONOBJ
from flask import Blueprint, session, app, current_app
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from blog.auth import login_required
from blog.db import get_db, Category, User, Post
import json

bp = Blueprint("blog", __name__)
UPLOADS_PATH = 'static/media'

def base_load(view):
    """View decorator that fill what is needed for basic functional like menu"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        g.category = Category.objects()

        return view(**kwargs)

    return wrapped_view

@base_load
@bp.route("/")
def index():
    user = g.user
    return render_template("blog/index.html", data=get_essentials())

@base_load
@bp.route("/create")
def create_post():
    return render_template("blog/create.html", data=get_essentials())

@base_load
@bp.route("/user")
def user():
    return render_template("blog/user.html")

@base_load
def get_essentials():
    data = dict()
    data['user'] = g.user if g.user else None
    data['category'] = Category.objects()
    return data

@base_load
@bp.route("/category/ajax")
def category_ajax():
    return {'category': [[str(obj.id), obj.title, str(obj.parent.id) if "parent" in obj else False,
                          [child.title for child in obj.child] if "child" in obj else False] for obj in
                         Category.objects()]}

@base_load
@bp.route("/category/add/ajax", methods=("GET", "POST"))
def category_add_ajax():
    if request.method == "POST":
        category_text = request.form['text']
        category_parent = request.form['parent']
        new_category = Category()
        new_category.title = category_text
        print(category_parent)
        if category_parent == 'بدون والد':
            new_category.save()
            parent = None
        else:

            new_category.parent = Category.objects(id=ObjectId(category_parent))[0]
            new_category.save()
            parent = Category.objects(id=ObjectId(category_parent))[0]
            parent.child += Category.objects(id=new_category.id)
            parent.save()
        # Category.objects(id=new_category.id)

        return {"self": str(new_category.id), "parent": str(parent.id) if parent is not None else None}


@bp.route("/post/draft/ajax", methods=("GET", "POST"))
def create_draft_post():
    new_post = Post()
    new_post.user = g.user
    new_post.draft = True
    new_post.save()
    return str(new_post.id)


@bp.route("/post/fetch/media/ajax", methods=("GET", "POST"))
def fetch_media():
    post_id = request.form['post_id']
    try:
        post = Post.objects(id=ObjectId(post_id)).get()
    except mongoengine.DoesNotExist:
        return False

    # return {'images': ['http://127.0.0.1:5000/static/media/post/0.Cover_.Zimmer-768x488.jpg','http://127.0.0.1:5000/static/media/post/0.Cover_.Zimmer-768x488.jpg','http://127.0.0.1:5000/static/media/post/0.Cover_.Zimmer-768x488.jpg','http://127.0.0.1:5000/static/media/post/0.Cover_.Zimmer-768x488.jpg','http://127.0.0.1:5000/static/media/post/0.Cover_.Zimmer-768x488.jpg']}
    return {'images': [image for image in post.images]}
    # return {'images': post.images}


@bp.route("/post/upload/media/ajax", methods=("GET", "POST"))
def upload_pic():
    post_id = request.form['post_id']
    print(post_id)
    file = request.files['media']
    try:
        post = Post.objects(id=ObjectId(post_id)).get()
        address = f'static/users/{g.user.username}/{file.filename}'
        file.save(os.path.join(current_app.root_path, f'static/users/{g.user.username}/{file.filename}'))
        post.images.append(address)
        post.save()

        return address
    except mongoengine.DoesNotExist:
        print('failed')

    return 'done'


# @bp.route("/post/create/ajax", methods=("GET", "POST"))
# def create_post_ajax():
#     data=request.args
#     form=request.form.get('title')
#     print(data,form)
#     return "done"