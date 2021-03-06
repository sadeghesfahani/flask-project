import ast
import functools
import os
from pprint import pprint

import mongoengine
from bson import ObjectId
from flask import Blueprint, session, app, current_app
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import abort
from jinja2 import environment, pass_eval_context
from werkzeug.utils import secure_filename
from blog.auth import login_required
from blog.db import Category, User, Post, Comment
from mongoengine.queryset.visitor import Q
import json
from datetime import datetime

bp = Blueprint("blog", __name__)
UPLOADS_PATH = 'static/media'


def base_load(view):
    """
    this decorator has been designed to get ride of redundancy of passing basic data
    toward pages
    :return: passing category data so far
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        g.category = Category.objects()

        return view(**kwargs)

    return wrapped_view


# @pass_eval_context
# def get_user(user_id):
#     user = User.objects(id=ObjectId(user_id)).get()
#     return user

# ############# NOT USED ################
# tag finder api
# @bp.route("/check_tag")
# def check_tag():
#     tag_name = request.args.get('tag')
#     current_app.logger.debug(request.args)
#     tags = Post.objects(tags=tag_name)
#     if tags:
#         return {'tags': tags}
#         return "tags existed"
    # return {'new_tag': tag_name}
# ######################################

@bp.route("/tag/<tag_name>")
def tag(tag_name):
    posts = Post.objects(tags=tag_name)

    # TODO: querying for comments with that tag
    # ###### DOES NO WORK LIKE THIS ##########
    # for post in Post.objects:
    #     for comment in post.comment:
    #         current_app.logger.debug(comment)
    #         if tag_name in comment.tags:
    #             posts.append(comment)
    # ##########################################

    return render_template('blog/category.html', posts=posts, tag=tag_name)


@bp.route("/category/<cat>")
@base_load
def category(cat):
    try:
        my_cat = Category.objects(id=ObjectId(cat)).get()
    except mongoengine.DoesNotExist:
        abort(404, "This  does not exist")
    return render_template('blog/category.html', posts=Post.objects(category=my_cat), cat=my_cat)


@bp.route("/")
@base_load
def index():
    slider_posts = Post.objects(slider=True)
    category_post_list = list()
    index_posts = dict()
    for category in Category.objects(parent=None):
        index_posts[category.title] = list()
        if 'child' in category:
            posts = Post.objects.filter(category__contains=category.id)
            posts = [x for x in posts if x != [] and x.published and x.index]
            if posts:
                [index_posts[category.title].append(post) for post in posts]
            for children in category['child']:
                posts = Post.objects.filter(category__contains=children.id)
                posts = [x for x in posts if x != [] and x.published and x.index]
                if posts:
                    [index_posts[category.title].append(post) for post in posts]
        else:
            posts = Post.objects.filter(category__contains=category.id)
            posts = [x for x in posts if x != [] and x.published and x.index]
            if posts:
                [index_posts[category.title].append(post) for post in posts]

        # #print(category_post_list)
        # make_it_tuple = tuple(category_post_list)
        # #print(make_it_tuple)
        # category_post_list = list(make_it_tuple)
        # index_posts[category.title] = category_post_list
        # category_post_list = list()
    print(index_posts)

    posts = {
        'index': index_posts,
        'slider': slider_posts
    }
    return render_template("blog/index.html", posts=posts)


@bp.route("/create/")
@login_required
@base_load
def create_post():
    return render_template("blog/create.html")


@bp.route("/edit/<string:seo>")
@login_required
@base_load
def edit_post(seo):
    try:
        post = Post.objects(seo=seo).get()
        print(str(post.id))
        category_to_send = list()
        for category in post.category:
            category_to_send.append(category.id)
        print(category_to_send)
        print(post)
    except mongoengine.DoesNotExist:
        pass
    if g.user == post.user:
        return render_template("blog/edit.html", post=post, category=category_to_send)


@bp.route("/user")
@login_required
@base_load
def user():
    return render_template("blog/user.html")


@bp.route("/category/ajax")
def category_ajax():
    """
    this section fetches all category data exist in database and pass it to the
    Front-end for the further uses
    :return: a dictionary consists of list of all categories in detail
    """
    return {'category': [[str(obj.id), obj.title, str(obj.parent.id) if "parent" in obj else False,
                          [child.title for child in obj.child] if "child" in obj else False] for obj in
                         Category.objects()]}


@bp.route("/category/add/ajax", methods=("GET", "POST"))
def category_add_ajax():
    """
    this section add category to the category collections based on what
    Front-end passes by. if there is no parent if will be considered as
    first level category otherwise the parent will be added to the parent
    field and parent will be recalled and this new child will be added to
    its child list
    :return: a dictionary consists of created category id and its parent id
    """
    if request.method == "POST":
        category_text = request.form['text']
        category_parent = request.form['parent']
        new_category = Category()
        new_category.title = category_text
        print(category_parent)
        if category_parent == '???????? ????????':
            new_category.save()
            parent = None
        else:

            new_category.parent = Category.objects(id=ObjectId(category_parent))[0]
            new_category.save()
            parent = Category.objects(id=ObjectId(category_parent))[0]
            parent.child += Category.objects(id=new_category.id)
            parent.save()

        return {"self": str(new_category.id), "parent": str(parent.id) if parent is not None else None}


@bp.route("/post/draft/ajax", methods=("GET", "POST"))
def create_draft_post():
    """
    this section create a draft for uploading and storing uploaded pictures
    related to post
    :return: created post id
    """
    new_post = Post()
    new_post.user = g.user
    new_post.draft = True
    new_post.views = 0
    new_post.save()
    return str(new_post.id)


@bp.route("/post/fetch/media/ajax", methods=("GET", "POST"))
def fetch_media():
    """
    this section fetch all image addresses related to the specific post
    which is determined by Front-end
    :return: list of all related picture addresses
    """
    post_id = request.form['post_id']
    try:
        post = Post.objects(id=ObjectId(post_id)).get()
    except mongoengine.DoesNotExist:
        return False

    return {'images': [image for image in post.images]}


@bp.route("/post/upload/media/ajax", methods=("GET", "POST"))
def upload_pic():
    """
    this section uploads picture into user's directory and put (append) their address
    into the post database (images list)
    :return: uploaded picture address
    """
    # fetching data passed from Front-end
    post_id = request.form['post_id']
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


@bp.route("/post/upload/main-media/ajax",methods=("GET", "POST"))
def upload_main_pic():
    """
    this section upload main picture of the post into user directory
    and save it to the post data base (main_image)
    :return: saved picture address
    """

    # fetching data passed from Front-end
    post_id = request.form['post_id']
    file = request.files['media']
    try:
        post = Post.objects(id=ObjectId(post_id)).get()
        address = f'static/users/{g.user.username}/{file.filename}'
        file.save(os.path.join(current_app.root_path, f'static/users/{g.user.username}/{file.filename}'))
        post.main_image = address
        post.save()
        return address
    except mongoengine.DoesNotExist:
        print('failed')

    return 'done'


@bp.route("/post/create/ajax", methods=("GET", "POST"))
def create_post_ajax():
    """
    this section creates post or update changes if there is
    post_id in passed json, update part will run otherwise
    create part will run
    :return: true if successfull, false if it failed
    """
    decoded_data = request.json
    current_app.logger.debug(decoded_data)
    if 'post_id' in decoded_data:
        print("im here")
        post = Post.objects(id=ObjectId(decoded_data['post_id'])).get()
        post.title = decoded_data['title']
        post.category = [ObjectId(category) for category in decoded_data['category']]
        post.body = decoded_data['content']
        post.published = decoded_data['publish']
        post.slider = decoded_data['slider']
        post.index = decoded_data['index']
        post.seo = decoded_data['seo']
        post.draft = False
        post.tags = [tag_name for tag_name in decoded_data['tags']]
        post.save()
        return str(post.id)
    else:
        new_post = Post()
        new_post.user = g.user
        new_post.title = decoded_data['title']
        new_post.category = decoded_data['category']
        new_post.draft = False
        new_post.body = decoded_data['content']
        new_post.published = decoded_data['publish']
        new_post.slider = decoded_data['slider']
        new_post.index = decoded_data['index']
        new_post.seo = decoded_data['seo']
        new_post.views = 0
        new_post.tags = [tag_name for tag_name in decoded_data['tags']]
        new_post.save()
        return str(new_post.id)


@bp.route("/post/remove/media/ajax", methods=("GET", "POST"))
def remove_pic():
    """
    this section delete picture which had been already added
    to the user directory and post database (images list) with
    ajax technology
    :returns: nothing
    """

    # getting information from front end to work with
    post_id = request.form['post_id']
    address = request.form['address']

    # finding post with identified id and remove specified picture from it
    try:
        post = Post.objects(id=ObjectId(post_id)).get()
        post.images.remove(address)
        post.save()
        os.remove(os.path.join(current_app.root_path, address))
        return address
    except mongoengine.DoesNotExist:
        print('failed')

    return 'done'


@bp.route("/post/<seo>")
@base_load
def show_post(seo):
    """
    this section gets the seo and return the post data to show
    :param seo:
    :return: post data
    """
    try:
        post = Post.objects(seo=seo).get()
        user_own_post = post.user
        all_posts_count = Post.objects(user=user_own_post).count()
        if str(post.id) not in session:
            if 'views' not in post:
                post.views = 1
                post.save()
            else:
                post.views += 1
                post.save()
            session[str(post.id)] = True
    except mongoengine.DoesNotExist:
        pass

    return render_template("blog/post.html", post=post, count=all_posts_count)


@bp.route("/post/comment/add/ajax", methods=["GET", "POST"])
def add_comment():
    decoded_data = request.json
    current_app.logger.debug(decoded_data)
    comment = decoded_data['comment']
    comment_user = g.user
    post = decoded_data['post_id']
    new_comment = Comment()
    new_comment.user = comment_user
    new_comment.text = comment
    new_comment.tags = [tag_name for tag_name in decoded_data['tags']]
    post = Post.objects(id=post).get()
    post.comment.append(new_comment)
    post.save()
    return "done"


@bp.route("/profile/")
@login_required
@base_load
def profile():
    # try:
    user_posts = Post.objects(user=ObjectId(g.user.id),draft__ne=True)
    print(user_posts)
    return render_template("user_doshboard.html", user_posts=user_posts)
    # except:
    #     user_posts = None
    #     return render_template("user_doshboard.html", user_posts=user_posts)


@bp.route("/edit-profile/",methods=("GET", "POST"))
@login_required
@base_load
def edit_profile():
    # get info from form and save it
    # ...

    if request.method == "POST":
        if request.form['info'] == 'file':
            file = request.files['choice-avatar']
            user = User.objects(username=g.user.username).get()
            address = f'static/users/{g.user.username}/{file.filename}'
            file.save(os.path.join(current_app.root_path, f'static/users/{g.user.username}/{file.filename}'))
            # user.avatar.append(address)
            user.avatar = address
            user.save()

            return render_template("user_doshboard.html")
        elif request.form['info'] == 'text':
            first_name = request.form['first-name']
            last_name = request.form['last-name']
            password = request.form['password']
            email = request.form['email']
            user = User.objects(username=g.user.username).get()
            if first_name not in [None, "", " "] and first_name.isnumeric() == False:
                user.first_name = first_name
                user.save()
            if last_name not in [None, "", " "] and first_name.isnumeric() == False:
                user.last_name = last_name
                user.save()
            if password not in [None, ""]:
                user.password = password
                user.save()
            if email not in [None, ""]:
                user.email = email
                user.save()

            return render_template("user_doshboard.html")
    else:
        return render_template("user_doshboard.html")


@bp.route("/post/like/add/ajax", methods=("GET", "POST"))
def add_like():
    post_id = request.form['post_id']
    user_who_act = User.objects(id =g.user.id).get()
    post = Post.objects(id=post_id).get()

    if user_who_act in post.dislike:
        post.dislike.remove(user_who_act)

    if user_who_act in post.likes:
        pass
    else:
        post.likes.append(user_who_act)

    post.save()
    return "done"


@bp.route("/post/dislike/add/ajax", methods=("GET", "POST"))
def add_dislike():
    post_id = request.form['post_id']
    user_who_act = User.objects(id =g.user.id).get()
    post = Post.objects(id=post_id).get()

    if user_who_act in post.likes:
        post.likes.remove(user_who_act)

    if user_who_act in post.dislike:
        pass
    else:
        post.dislike.append(user_who_act)

    post.save()
    return "done"

@bp.route("/post-delete/", methods=("GET", "POST"))
def post_delete():
    if request.method == 'POST':
        try:
            post_id = request.form['post_id']
            print(post_id)
            post = Post.objects(id=ObjectId(post_id)).get()
            post.delete()
            # post.title.remove()
            # post.body.remove()
            # post.user.remove()
            # post.category.remove()
            # post.main_image.remove()
            # post.images.remove()
            # post.likes.remove()
            # post.dislike.remove()
            # post.time.remove()
            # post.comment.remove()
            # post.draft.remove()
            # post.published.remove()
            # post.index.remove()
            # post.slider.remove()
            # post.seo.remove()
            # post.save()
            return render_template("user_doshboard.html")
        except mongoengine.DoesNotExist:
            abort(404, "Post Doesn't exist")


@bp.route("/search", methods=("GET", "POST"))
def search():
    index_posts = dict()

    if request.method == "POST":
        search_word = request.form["search-box"]

        for category in Category.objects(parent=None):
            index_posts[category.title] = list()
            if 'child' in category:
                all_posts = Post.objects()
                posts = Post.objects((Q(body__icontains=search_word) | Q(tags=search_word) | Q(title=search_word)))
                posts = [post for post in posts if post != [] and post.published and post.index]
                posts_that_search_word_in_author = [post for post in all_posts if post not in posts and post.body != None and search_word in post.user.first_name and post != [] and post.published and post.index]
                posts = posts + posts_that_search_word_in_author
                if posts:
                    [index_posts[category.title].append(post) for post in posts]
                for children in category['child']:
                    if posts:
                        [index_posts[category.title].append(post) for post in posts]
            else:
                all_posts = Post.objects()
                posts = Post.objects((Q(body__icontains=search_word) | Q(tags=search_word) | Q(title=search_word)))
                posts = [post for post in posts if post != [] and post.published and post.index]
                posts_that_search_word_in_author = [post for post in all_posts if post not in posts and post.body != None and search_word in post.user.first_name and post != [] and post.published and post.index]
                posts = posts + posts_that_search_word_in_author
                if posts:
                    [index_posts[category.title].append(post) for post in posts]

        posts = {
            'index': index_posts
        }
        return render_template("blog/index.html", posts=posts)
