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
import pymongo







bp = Blueprint("blog", __name__)
UPLOADS_PATH = 'static/media'

#create database
#myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#db = myclient["mydatabase"]

#create users table
#user_col = db["users"]



@bp.route("/")
def index():

    return render_template("blog/index.html")

@bp.route("/profile")
def profile():
    user_posts = None
    other_posts = None

    user = {}
    user_posts = []
    if len(user_posts) > 5:
        recent_posts = user_posts[-1,-5,-1]
    else:
        other_posts = user_posts[:-5]
    return  render_template("user_doshboard.html", recent_posts=[1,2,3,4,5], other_post=[1,2,3,4])


@bp.route("/edit-profile/<username>")
def edit(username):
    user = {}
    #get info from form and save it
    return render_template("edit_profile.html", user={"first_name":"Sina", "last_name":"Esmaili", "username":"Sina123", "password":"12345678", "email":"sina@emaili.com", "phone":"09168581319"})

