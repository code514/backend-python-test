import sqlite3

from flask import Flask, g


# configuration
DATABASE = '/tmp/alayatodo.db'
SECRET_KEY = 'development key'


app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        g._db = db
    return db


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()


import alayatodo.views  # noqa: E402,F401
