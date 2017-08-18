from application import db, login_manager
import random
from datetime import datetime


class Image(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    url = db.Column(db.String(512))
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.create_date = datetime.now()

    def __repr__(self):
        return '<Image {} {}>'.format(self.id, self.url)


class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(32))
    salt = db.Column(db.String(32))
    head_url = db.Column(db.String(256))
    images = db.relationship('Image', backref='user', lazy='dynamic')
    comments = db.relationship('Comment')

    def __init__(self, username, password, salt=''):
        self.username = username
        self.password = password
        self.salt = salt
        self.head_url = 'https://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'

    def __repr__(self):
        return '<User {} {}>'.format(self.id, self.username)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Comment(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.INTEGER, db.ForeignKey('image.id'))
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    status = db.Column(db.INTEGER, default=0)  # 1为逻辑删除状态
    user = db.relationship('User')

    def __init__(self, content, user_id, image_id):
        self.content = content
        self.user_id = user_id
        self.image_id = image_id

    def __repr__(self):
        return '<Comment {} {}>'.format(self.id, self.content)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
