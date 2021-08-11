from os.path import join, dirname, realpath
from bson import ObjectId
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
from blog.db import get_db

bp = Blueprint("blog", __name__)
UPLOADS_PATH = 'static/media'


@bp.route("/")
def index():
    user=g.user
    return render_template("blog/index.html",data=get_essentials())



@bp.route("/create")
def create_post():
    return render_template("blog/create.html")


@bp.route("/user")
def user():

    return render_template("blog/user.html")



def get_essentials():
    data=dict()
    data['user']= g.user if g.user else None
    return data

