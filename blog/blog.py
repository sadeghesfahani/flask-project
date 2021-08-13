from bson import ObjectId, BSONOBJ
from datetime import datetime
from pprint import pprint
from flask import (
    current_app, Blueprint, flash, g, redirect, render_template, request, url_for
)

from blog.auth import login_required
from blog.db import get_db, Post, Category
import json

bp = Blueprint("blog", __name__)
UPLOADS_PATH = 'static/media'


@bp.route("/")
def index():
    db = get_db()
    sliders = dict()
    for post in Post.objects(index=True):
        try:
            sliders[post.category.title] = [*sliders.get(post.category.title), post]
        except TypeError:
            sliders[post.category.title] = [post]
    current_app.logger.debug(pprint(sliders))
    data = {
        'user': g.user,
        'posts': Post.objects().order_by("created"),
        'sliders': sliders
    }
    return render_template("blog/index.html", data=data)


# ---------------------------------------------- 3oop Code -------------------------------------

# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None
#
#         if not title:
#             error = 'Title is required.'
#
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             new_post = Post(
#                 title=title,
#                 body=body,
#                 author=g.user,
#                 created=datetime.now()
#             )
#             new_post.save()
#             return redirect(url_for('blog.index'))
#
#     return render_template('blog/create.html')
#
#
# def get_post(id, check_author=True):
#     post = Post.objects(id=str(id)).get()
#
#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")
#
#     if check_author and post['author'] != g.user['username']:
#         abort(403)
#
#     return post
#
#
# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)
#
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None
#
#         if not title:
#             error = 'Title is required.'
#
#         if error is not None:
#             flash(error)
#         else:
#             post.title = title
#             post.body = body
#             post.save()
#             return redirect(url_for('blog.index'))
#
#     return render_template('blog/update.html', post=post)
#
# -------------------------------- 3oop Code -----------------------

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_post():
    db = get_db()
    data = {'user': g.user, 'category': Category.objects()}
    return render_template("blog/create.html", data=data)


@bp.route("/user")
def user():
    db = get_db()
    return render_template("blog/user.html")


@bp.route("/category/ajax")
def category_ajax():
    db = get_db()
    return {'category': [[str(obj.id), obj.title, str(obj.parent.id) if "parent" in obj else False,
                          [child.title for child in obj.child] if "child" in obj else False] for obj in
                         Category.objects()]}


@bp.route("/category/add/ajax", methods=("GET", "POST"))
def category_add_ajax():
    db = get_db()
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
