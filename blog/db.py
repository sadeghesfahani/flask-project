from flask import g
from pymongo import MongoClient


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    client = MongoClient('localhost', 27017)
    if "db" not in g:
        g.db = client.blog
    return g.db



