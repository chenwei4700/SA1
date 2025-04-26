from flask import Blueprint, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()
post_bp = Blueprint('post', __name__, template_folder='templates')

taiwan_tz = pytz.timezone('Asia/Taipei')

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(taiwan_tz))

    def __repr__(self):
        return f'<Post {self.title}>'

@post_bp.route('/post')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@post_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title or not content:
            flash('標題和內容都是必填的！')
            return redirect('/post/new')

        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        flash('貼文已成功發布！')
        return redirect('/post')

    return render_template('new_post.html')

@post_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.created_at = datetime.now(taiwan_tz)

        if not post.title or not post.content:
            flash('標題和內容都是必填的！')
            return redirect(f'/post/{post.id}/edit')

        db.session.commit()
        flash('貼文已成功更新！')
        return redirect('/post')

    return render_template('edit_post.html', post=post)

@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('貼文已成功刪除！')
    return redirect('/post')
