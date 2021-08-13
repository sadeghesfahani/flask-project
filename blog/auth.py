import functools
import mongoengine
from bson import ObjectId
from flask import Blueprint, flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from blog.db import create_user, User

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
        g.user = User.objects(id=ObjectId(user_id)).get()


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        if not User.objects(username=request.form["username"]).count():
            create_user(request.form["username"], request.form["password"], request.form["first_name"],
                        request.form["last_name"], request.form["email"], request.form["address"],
                        request.form["instagram"], request.form["telegram"])
            return redirect(url_for('index'))
    return render_template("auth/login.html", req='register')


@bp.route("/login", methods=("GET", "POST"))
def login():
    error = None
    if request.method == "POST":
        username = request.form["username_login"]
        password = request.form['password_login']
        try:
            user = User.objects(username=username).get()
        except mongoengine.DoesNotExist:
            error = True
            user = None

        if user is None:
            error = True
        elif not check_password_hash(user['password'], password):
            error = True

        if error is None:
            session.clear()
            session['user_id'] = str(user.id)
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', req='Login')



@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))


@bp.route('/check', methods=("GET", "POST"))
def check_username():
    if request.method == "POST":
        if User.objects(username=request.form['username']).count():
            return 'exist'
        else:
            return 'ok'
    else:
        return redirect(url_for('index'))



