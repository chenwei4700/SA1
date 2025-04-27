from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

post_bp = Blueprint('post', __name__)

db = SQLAlchemy()

taiwan_tz = pytz.timezone('Asia/Taipei')

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(taiwan_tz))
    author_account = db.Column(db.String(100), nullable=False)  # ✅ 新增，記錄誰發的

    def __repr__(self):
        return f'<Post {self.title}>'
    
@post_bp.route('/')
def index():
    if 'user' not in session:
        return redirect('/')

    posts = Post.query.filter_by(author_account=session['user']).order_by(Post.created_at.desc()).all()
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    return render_template('index.html', posts=posts, avatar=avatar, name=name)

# 新增貼文
@post_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_account = session['user']  # ✅ 從 session 拿目前登入的人

        new_post = Post(title=title, content=content, author_account=author_account)
        db.session.add(new_post)
        db.session.commit()

        flash('成功新增貼文！')
        return redirect(url_for('post.index'))

    return render_template('new_post.html', name=name, avatar=avatar)


@post_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.created_at = datetime.now(taiwan_tz)

        if not post.title or not post.content:
            flash('標題和內容都是必填的！')
            return redirect(url_for('post.edit_post', post_id=post.id))  

        db.session.commit()
        flash('貼文已成功更新！')
        return redirect(url_for('post.index'))  

    return render_template('edit_post.html', post=post, avatar=avatar, name=name)

@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('貼文已成功刪除！')

    # 判斷是從哪個頁面來
    next_page = request.form.get('next')  # 抓隱藏欄位
    if next_page == 'interact':
        return redirect(url_for('post.interact'))
    else:
        return redirect(url_for('post.index'))


# @post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
# def delete_post(post_id):
#     post = Post.query.get_or_404(post_id)
#     db.session.delete(post)
#     db.session.commit()
#     flash('貼文已成功刪除！')
#     return redirect(url_for('post.index'))  

@post_bp.route('/interact')
def interact():
    if 'user' in session:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        avatar = session.get('avatar', 'images/avatar.png')
        name = session.get('name', '未登入')
        return render_template('interact.html', posts=posts, avatar=avatar, name=name)
    else:
        return redirect('/')


