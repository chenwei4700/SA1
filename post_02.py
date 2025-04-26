from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz  # 時區

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'  # 使用 posts.db 作為資料庫
db = SQLAlchemy(app)

# 設定台灣時區
taiwan_tz = pytz.timezone('Asia/Taipei')

class Post(db.Model):  # 交流貼文
    __tablename__ = 'posts'  # 明確指定資料表名稱
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(taiwan_tz))

    def __repr__(self):
        return f'<Post {self.title}>'

with app.app_context():
    db.create_all()

@app.route('/')  # 顯示發布的貼文
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()  # 依照發布時間排序(新到舊)
    return render_template('index.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])  # 新增貼文
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash('標題和內容都是必填的！')
            return redirect('/post/new')  # 靜態的路由，取代 url_for
        
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        flash('貼文已成功發布！')
        return redirect('/')  # 靜態的路由，取代 url_for
    
    return render_template('new_post.html')

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])  # 編輯貼文
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.created_at = datetime.now(taiwan_tz)  # 更新為當前台灣時間
        
        if not post.title or not post.content:
            flash('標題和內容都是必填的！')
            return redirect(f'/post/{post.id}/edit')  # 靜態的路由，取代 url_for
        
        db.session.commit()
        flash('貼文已成功更新！')
        return redirect('/')  # 靜態的路由，取代 url_for
    
    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])  # 刪除貼文
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('貼文已成功刪除！')
    return redirect('/')  # 靜態的路由，取代 url_for

if __name__ == '__main__':
    app.run(debug=True)
