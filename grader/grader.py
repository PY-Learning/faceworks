# -*- encoding: utf-8 -*-

import os
import random
import string
import sys
from datetime import datetime

import click
from flask import Flask, request, render_template, redirect, url_for, abort, send_from_directory
from flask_login import LoginManager, current_user, login_user
from sqlalchemy import Column, DateTime, Integer, String, create_engine
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps

engine = create_engine('sqlite:///test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
login_manager = LoginManager()

app = Flask('grader')
app.config.from_pyfile('config.py')
if 'FACEWORKS_GRADER_CONFIG' in os.environ:
    app.config.from_envvar('FACEWORKS_GRADER_CONFIG')

login_manager.init_app(app)
# Model Layer #


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    pwd = Column(String(120))
    progress = Column(Integer)

    def __init__(self, name=None):
        self.name = name
        self.pwd = ''.join(random.choices(string.ascii_letters, k=8))
        self.progress = 0

    def __repr__(self):
        return '<User %d: %r>' % (self.id, self.name)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    md5 = Column(String(32), unique=True)
    count = Column(Integer)

    def __init__(self, md5=None):
        self.md5 = md5
        self.count = 0

    def __repr__(self):
        return '<Image %d: %r>' % (self.id, self.md5)


class Score(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True)
    user = Column(Integer)
    image = Column(Integer)
    score = Column(Integer)
    ts = Column(DateTime)
    nouce = Column(Integer)

    def __init__(self, user, image, score=0):
        self.user = user
        self.image = image
        self.score = score
        self.ts = datetime.utcnow()
        self.nouce = random.randint(0, 10000)

    def __repr__(self):
        return '<Score %d->%d, %d>' % (self.user, self.image, self.score)


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).filter(User.id == int(user_id)).one_or_none()

# Logic Layer #


def _init_db():
    Base.metadata.create_all(bind=engine)


def _add_score(user, image):
    # add score records
    score = Score(user, image)
    db_session.add(score)
    db_session.commit()


def _add_image(md5):
    # add to every user
    image = Image(md5=md5)
    db_session.add(image)
    db_session.commit()
    for row in db_session.query(User.id):
        score = Score(row.id, image.id)
        db_session.add(score)
    db_session.commit()
    return image


def _add_user(name):
    # add every image
    user = User(name)
    db_session.add(user)
    db_session.commit()
    for row in db_session.query(Image.id):
        score = Score(user.id, row.id)
        db_session.add(score)
    db_session.commit()
    return user


def _put_score(user, image, score):
    # put score
    ins = db_session.query(Score).filter(
        Score.user == user, Score.image == image).one()
    if score != 0 and ins.score == 0:
        image = db_session.query(Image).filter(Image.id == image).one()
        image.count += 1
        db_session.add(image)
    ins.score = score
    ins.ts = datetime.utcnow()
    db_session.add(ins)
    db_session.commit()


def _select_image(user):
    # Select a image for a user
    return db_session.query(Score).filter(Score.user == user, Score.score == 0).order_by(Score.nouce).first()


def _get_user_process(user):
    total = db_session.query(sqlalchemy.func.count(
        Score.id)).filter(Score.user == user)
    zeros = db_session.query(sqlalchemy.func.count(Score.id)).filter(
        Score.user == user, Score.score == 0)
    return total[0][0], zeros[0][0]


def _get_sys_process():
    total = db_session.query(sqlalchemy.func.count(Image.id))
    zeros = db_session.query(
        sqlalchemy.func.count(Image.id)).filter(Image.count < 3)
    return total[0][0], zeros[0][0]


# View Layer #

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/login')
        else:
            return func(*args, **kwargs)
    return wrapper


@app.route('/')
def index_view():
    if not current_user.is_authenticated:
        return redirect('/login')
    else:
        return redirect('/score')


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'GET':
        if current_user.is_anonymous:
            return render_template('login.html')
        else:
            return redirect('/score')
    else:
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        if not pwd or not username:
            abort(400)
        r = db_session.query(User).filter(
            User.name == username, User.pwd == pwd).one_or_none()
        if not r:
            abort(403)
        if r.name == username:
            login_user(r)
            return redirect('/score')
        else:
            abort(400)


@app.route('/score', methods=['GET'])
@login_required
def score_route_view():
    next_image = _select_image(int(current_user.get_id()))
    if not next_image:
        return redirect('/finished')
    return redirect('/score/%s' % next_image.id)


@app.route('/score/<vid>', methods=['GET', 'POST'])
@login_required
def score_view(vid):
    if request.method == 'GET':
        image = db_session.query(Image).filter(
            Image.id == int(vid)).one_or_none()
        if not image:
            return redirect('/score')
        return render_template('score.html', image_url='/images/' + image.md5,
                               sys_process=_get_sys_process(),
                               user_process=_get_user_process(int(current_user.get_id())))
    else:
        score = request.form.get('score')
        if score == None:
            abort(405)
        score = int(score)
        _put_score(int(current_user.get_id()), int(vid), score=score)
        return redirect('/score')


@app.route('/finished', methods=['GET'])
@login_required
def finish_view():
    return render_template('finished.html', sys_process=_get_sys_process())


@app.route('/images/<filename>')
def image_view(filename):
    return send_from_directory('images', filename)

# Command Layer #


@click.group()
def cli():
    pass


@cli.command()
def run():
    app.run('localhost', 5000, debug=True)


@cli.command()
@click.argument('name')
def add_user(name):
    user = _add_user(name)
    print("New User %s, password is %s" % (user.name, user.pwd))


@cli.command()
@click.argument('path', nargs=-1)
def add_image(path):
    for i in path:
        name = os.path.basename(i)
        _add_image(name)


@cli.command()
def init_db():
    _init_db()


def main():
    cli()

if __name__ == '__main__':
    main()
