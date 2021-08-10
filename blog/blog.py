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

    return render_template("blog/index.html")


