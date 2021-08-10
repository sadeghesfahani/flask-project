import functools
import re
from typing import NoReturn

from bson import ObjectId
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from blog.db import get_db
import pymongo


#create database
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["mydatabase"]

#create users table
user_col = db["users"]


#create database
#db = get_db()
#create users table
#user_col = db["users"]


bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().user.find_one({"_id": ObjectId(user_id)})



@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    else:
        
        session["username"] = request.form["username"]
        
        user_info = {
            "first_name":request.form["first_name"],
            "last_name":request.form["last_name"],
            "username":request.form["username"],
            "password":generate_password_hash(request.form["password"],"sha256"),
            "email":request.form["email"],
            "addres":request.form["address"],
            "social":[{
                "instagram":request.form["instagram"],
                "telegram":request.form["telegram"]
            }]
        }

        user_col.insert_one(user_info)

        name= request.form["first_name"]

        return render_template("add_user.html", name=name)


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    else:
        username = request.form["username_login"]
        if username in session["username"]:
            user = user_col.find({"username":username})
            user = [i for i in user]

            if not check_password_hash(user[0]["password"], request.form["password_login"]):
                error = "inccorect password"
            elif user[0]["username"] != request.form["username_login"]:
                error = "inccorect username"
            else:
                error = None
        else:
            error = "username not avilable"
        return render_template("login.html", error=error)
     

@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))



