from application import app, db
from application.models import User, Image, Comment
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
import random, hashlib, json
import os, uuid
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def index():
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=1, per_page=10)
    return render_template('index.html', images=paginate.items, has_next=paginate.has_next)


@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    msg = ''
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page)
    map = {'has_next': paginate.has_next, 'msg_length':len(msg), 'msg':msg}
    images = []
    comments = []
    for image in paginate.items:
        images.append({
            'id': image.id, 'url': image.url, 'comments_count': len(image.comments),
            'create_date': str(image.create_date), 'user_id': image.user_id,
            'username': image.user.username, 'head_url': image.user.head_url
        })
        comments.append([{
            'content': comment.content, 'comment_user_id': comment.user_id, 'comment_username': comment.user.username
        } for comment in image.comments])

    map['images'] = images
    map['comments'] = comments
    return json.dumps(map)


@app.route('/image/<int:image_id>')
@login_required
def image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return redirect('/')

    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user is None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3)
    return render_template('profile.html', user=user, images=paginate.items, has_next=paginate.has_next)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        images.append({'id': image.id, 'url': image.url, 'comment_count': len(image.comments)})
    map['images'] = images
    return json.dumps(map)


@app.route('/regloginpage/')
def regloginpage(msg=''):
    if current_user.is_authenticated:
        return redirect('/')

    for cate, m in get_flashed_messages(with_categories=True, category_filter=['reglogin']):
        msg += m
    return render_template('login.html', msg=msg, next=request.form.get('next'))


@app.route('/reg/', methods=['POST'])
def register():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()

    if username == '' or password == '':
        return redirect_msg('/regloginpage/', '用户名或密码不能为空!', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user is not None:
        return redirect_msg('/regloginpage/', '用户名已经存在!', 'reglogin')

    salt = '.'.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz', 10))
    m = hashlib.md5()
    m.update((password + salt).encode('utf-8'))
    password = m.hexdigest()
    session = db.Session(bind=db.get_engine(app))
    user = User(username, password, salt)
    session.add(user)
    session.commit()

    login_user(user)
    next = request.form.get('next')
    if next and next.startswith('/'):
        return redirect(next)

    return redirect('/')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


@app.route('/login/', methods=['POST'])
def login():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    if username == '' or password == '':
        return redirect_msg('/regloginpage/', '用户名或密码不能为空!', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect_msg('/regloginpage/', '用户名不存在!', 'reglogin')

    m = hashlib.md5()
    m.update((password + user.salt).encode('utf-8'))
    if m.hexdigest() != user.password:
        return redirect_msg('/regloginpage/', '密码错误!', 'reglogin')

    login_user(user)
    next = request.form.get('next')
    if next and next.startswith('/'):
        return redirect(next)
    return redirect('/')


@app.route('/addcomment/', methods=['POST'])
def post_comment():
    comment = request.form.get('content')
    image_id = request.form.get('image_id')

    session = db.Session(bind=db.get_engine(app))
    comment = Comment(comment, current_user.id, image_id)
    session.add(comment)
    session.commit()

    return json.dumps({
        'code': 0, 'id': comment.id, 'content': comment.content,
        'username': comment.user.username, 'user_id': comment.user_id
    })


@app.route('/loadmorecomment/', methods=['POST'])
def load_more():
    image_id = request.form.get('image_id')
    start = int(request.form.get('start'))
    data_size = int(request.form.get('data_size'))

    paginate = Comment.query.filter_by(image_id=image_id).limit(data_size).offset(start).all()
    if paginate is None:
        return json.dumps({'code':1, 'msg':'No data anymore!'})

    map = {'code':0}
    comments = []
    for comment in paginate:
        comments.append({
            'id': comment.id, 'content': comment.content,
            'username': comment.user.username, 'user_id': comment.user_id
        })
    map['comments'] = comments
    return json.dumps(map)


@app.route('/upload/', methods=['POST'])
def upload():
    print(request.files)
    file = request.files['file']
    print(file)
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-','') + '.' + file_ext
        url = save_local(file, file_name)
        if url:
            session = db.Session(bind=db.get_engine(app))
            session.add(Image(url, current_user.id))
            session.commit()

    return redirect('/profile/{}'.format(current_user.id))


@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


def redirect_msg(target, msg, category):
    if msg is not None:
        flash(msg, category=category)
    return redirect(target)


def save_local(file, file_name):
    save_path = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_path, file_name))
    return '/image/' + file_name