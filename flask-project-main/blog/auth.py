import functools
from os import error
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
from flask import Flask

from flask_mail import Mail, Message

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from blog.db import get_db
import pymongo

#------- this codes are for send email -----------
app = Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sinaesmaili216@gmail.com'
app.config['MAIL_PASSWORD'] = 'rqbtkkehicgpelrf'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
#-----------------------------------



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








    

#create 100 random code to send to user email to register 
import random
code = random.randint(111111,999999)


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        
        #check if username exist
        if not user_col.find({"username":request.form["username"]}):
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

            email = request.form.get("email")
            msg = Message('Register Code', sender='sinaesmaili216@gmail.com', recipients=[email])
            msg.body = f"yor code for register is {code}"
            mail.send(msg)

            user_col.insert_one(user_info)
            flash("your account created successfuly")
        else:
            flash("username exist")


        return redirect(url_for("auth.get_code"))
        #return redirect(url_for("index"))
        
    return render_template("auth/register.html")





#The user does not need to have access to this view address
@bp.route("/get-code", methods=["GET", "POST"])
def get_code():
    if request.method == "POST":
        usercode = int(request.form["get_code"])
        if usercode == code:
            return redirect(url_for("index"))
        else:
            error = "inccorect code"
            flash(error)
    return render_template("enter_password.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    error = None
    if request.method == "POST": 
        error = None

        username = request.form["username_login"]
        user = user_col.find({"username":username})
        user = [i for i in user]

        if user:
            if not check_password_hash(user[0]["password"], request.form["password_login"]):
                error = "inccorect password"
            elif user[0]["username"] != request.form["username_login"]:
                error = "inccorect username"
            else:
                session["username"] = request.form["username_login"]
                return redirect(url_for("index"))
        else:
            error = "inccorect username"

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))



