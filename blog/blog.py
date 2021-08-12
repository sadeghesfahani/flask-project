from os.path import join, dirname, realpath
from bson import ObjectId, BSONOBJ
from flask import Blueprint, session
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from blog.auth import login_required
from blog.db import get_db, Category, User
import json

bp = Blueprint("blog", __name__)
UPLOADS_PATH = 'static/media'


@bp.route("/")
def index():
    user = g.user
    return render_template("blog/index.html", data=get_essentials())


@bp.route("/create")
def create_post():
    return render_template("blog/create.html", data=get_essentials())


@bp.route("/user")
def user():
    return render_template("blog/user.html")


def get_essentials():
    data = dict()
    data['user'] = g.user if g.user else None
    data['category'] = Category.objects()
    return data


@bp.route("/category/ajax")
def category_ajax():
    return {'category': [[str(obj.id), obj.title, str(obj.parent.id) if "parent" in obj else False,
                          [child.title for child in obj.child] if "child" in obj else False] for obj in
                         Category.objects()]}


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
            parent=None
        else:

            new_category.parent = Category.objects(id=ObjectId(category_parent))[0]
            new_category.save()
            parent = Category.objects(id=ObjectId(category_parent))[0]
            parent.child += Category.objects(id=new_category.id)
            parent.save()
        # Category.objects(id=new_category.id)

        return {"self":str(new_category.id),"parent":str(parent.id) if parent is not None else None}
