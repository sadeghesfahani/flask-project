import functools
import random
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
from email.message import EmailMessage
from blog.db import get_db
import smtplib

bp = Blueprint("auth", __name__, url_prefix="/auth")

# ------- this codes are for send email -----------
app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sinaesmaili216@gmail.com'
app.config['MAIL_PASSWORD'] = '$eyedsina335099'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# -----------------------------------


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
    if request.method == "POST":
        db = get_db()
        code = random.randint(111111, 999999)
        # check if username exist
        print(db.user.count({"username": request.form["username"]}))
        if not db.user.count({"username": request.form["username"]}):
            user_info = {
                "first_name": request.form["first_name"],
                "last_name": request.form["last_name"],
                "username": request.form["username"],
                "password": generate_password_hash(request.form["password"], "sha256"),
                "email": request.form["email"],
                "addres": request.form["address"],
                "social": [{
                    "instagram": request.form["instagram"],
                    "telegram": request.form["telegram"]
                }],
                'activated': False,
                'activation_code': code
            }

            db.user.insert_one(user_info)
            email = request.form.get("email")
            return redirect(url_for('index'))
        else:
            flash("username exist")
        return redirect(url_for("auth.login"))
        # return redirect(url_for("index"))

    return redirect(url_for('index'))


@bp.route("/login", methods=("GET", "POST"))
def login():
    error = None
    if request.method == "POST":
        error = None
        db = get_db()
        username = request.form["username_login"]
        user = db.user.find({"username": username})
        password = request.form['password_login']
        user = [i for i in user]
        print(user)
        if user:
            user = user[0]
            if user['username'] == username and check_password_hash(user['password'], password):
                # print(user['_id'])
                session['user_id'] = str(user['_id'])
                print("session done")
                return redirect(url_for('index'))
        else:
            error = "loginf failed"

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))


@bp.route('/check', methods=("GET", "POST"))
def check_username():
    if request.method == "POST":
        username = request.form['username']
        db = get_db()
        if db.user.count({'username': username}):
            return 'exist'
        else:
            return 'ok'
    else:
        return redirect(url_for('index'))
