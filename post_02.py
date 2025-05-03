from flask import Blueprint, render_template, request, redirect, flash, url_for, session
import mysql.connector
from datetime import datetime
import pytz
post_bp = Blueprint('post', __name__)
taiwan_tz = pytz.timezone('Asia/Taipei')

# ✅ 建立 MySQL 連線
def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        database='sa2-2',
        unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
    )

@post_bp.route('/')
def index():
    if 'user' not in session:
        return redirect('/')

    id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 查詢貼文，帶出 like_count
    cur.execute("""
    SELECT posts.*, 
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count
    FROM posts 
    WHERE user_id = %s 
    ORDER BY created_at DESC
    """, (id,))
    posts = cur.fetchall()

    # 查詢每篇貼文的留言
    for post in posts:
        cur.execute("""
            SELECT comments.*, Users.account AS author_account
            FROM comments
            JOIN Users ON comments.user_id = Users.user_id
            WHERE comments.post_id = %s
            ORDER BY comments.created_at DESC
        """, (post['post_id'],))
        post['comments'] = cur.fetchall()

    cur.close()
    conn.close()

    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')
    return render_template('index.html', posts=posts, avatar=avatar, name=name, id=id)


@post_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    user_id = session.get('user_id')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now(taiwan_tz)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO posts (title, content, created_at, user_id, is_alert, hashtag_id) VALUES (%s, %s, %s, %s, '0', NULL)",
                    (title, content, created_at, user_id))
        conn.commit()
        cur.close()
        conn.close()

        flash('成功新增貼文！')
        return redirect(url_for('post.index'))

    return render_template('new_post.html', name=name, avatar=avatar)



@post_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now(taiwan_tz)

        if not title or not content:
            flash('標題和內容都是必填的！')
            return redirect(url_for('post.edit_post', post_id=post_id))

        cur.execute("UPDATE posts SET title = %s, content = %s, created_at = %s WHERE post_id = %s",
                    (title, content, created_at, post_id))
        conn.commit()
        cur.close()
        conn.close()

        flash('貼文已成功更新！')
        return redirect(url_for('post.index'))

    cur.execute("SELECT * FROM posts WHERE post_id = %s", (post_id,))
    post = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit_post.html', post=post, avatar=avatar, name=name)

@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash('貼文已成功刪除！')
    next_page = request.form.get('next')
    return redirect(url_for('post.interact' if next_page == 'interact' else 'post.index'))

@post_bp.route('/interact')
def interact():
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 查詢所有貼文，帶出 like_count
    cur.execute("""
    SELECT posts.*, Users.user_name, images.file_path,
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count
    FROM posts
    JOIN Users ON posts.user_id = Users.user_id
    LEFT JOIN (
        SELECT user_id, MAX(uploadtime) AS latest
        FROM images
        GROUP BY user_id
    ) latest_img ON latest_img.user_id = Users.user_id
    LEFT JOIN images ON images.user_id = latest_img.user_id AND images.uploadtime = latest_img.latest
    ORDER BY posts.created_at DESC
    """)
    posts = cur.fetchall()

    # 針對每篇貼文查詢留言
    for post in posts:
        cur.execute("""
            SELECT comments.*, Users.account AS author_account
            FROM comments
            JOIN Users ON comments.user_id = Users.user_id
            WHERE comments.post_id = %s
            ORDER BY comments.created_at DESC
        """, (post['post_id'],))
        post['comments'] = cur.fetchall()

    cur.close()
    conn.close()

    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')

    return render_template('interact.html', posts=posts, avatar=avatar, name=name, id=id)

@post_bp.route('/interact/search', methods=['GET', 'POST'])
def search():
    keyword = request.args.get('keyword', '').strip()
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')
    if keyword:
        # 如果有搜尋關鍵字，則進行搜尋
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # 搜尋符合關鍵字的標題或內容
        cur.execute("""
    SELECT 
        posts.*, 
        Users.user_name, 
        images.file_path,
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count,
        comments.comment_id, comments.content AS comment_content, comments.created_at AS comment_created_at, comment_users.user_name AS comment_author
    FROM posts
    JOIN Users ON posts.user_id = Users.user_id
    LEFT JOIN (
        SELECT user_id, MAX(uploadtime) AS latest
        FROM images
        GROUP BY user_id
    ) latest_img ON latest_img.user_id = Users.user_id
    LEFT JOIN images ON images.user_id = latest_img.user_id AND images.uploadtime = latest_img.latest
    LEFT JOIN comments ON comments.post_id = posts.post_id
    LEFT JOIN Users AS comment_users ON comments.user_id = comment_users.user_id
    ORDER BY posts.created_at DESC, comments.created_at ASC
""")


        
        posts = cur.fetchall()
        cur.close()
        conn.close()
    else:
        # 如果沒有關鍵字，則顯示所有貼文
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT posts.*, Users.user_name
            FROM posts
            JOIN Users ON posts.user_id = Users.user_id
            ORDER BY posts.created_at DESC
        """)
        
        posts = cur.fetchall()
        cur.close()
        conn.close()

@post_bp.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        flash('請先登入才能按讚')
        return redirect(url_for('post.interact'))

    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()

    # 檢查是否已按過讚
    cur.execute("SELECT * FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
    like = cur.fetchone()

    if like:
        # 已經按過讚的話就取消讚
        cur.execute("DELETE FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
    else:
        # 沒按過就加入一個讚
        cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('post.interact'))

@post_bp.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash('請先登入才能留言')
        return redirect(url_for('post.interact'))

    user_id = session['user_id']
    content = request.form['content']
    created_at = datetime.now(taiwan_tz)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO comments (post_id, user_id, content, created_at) VALUES (%s, %s, %s, %s)",
                (post_id, user_id, content, created_at))
    conn.commit()
    cur.close()
    conn.close()

    flash('留言已發佈！')
    return redirect(url_for('post.interact'))

@post_bp.route('/post/<int:post_id>/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(post_id, comment_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE comment_id = %s", (comment_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash('留言已刪除！')
    next_page = request.form.get('next', 'interact')
    return redirect(url_for(f'post.{next_page}'))



    return render_template('interact.html', posts=posts, keyword=keyword, avatar=avatar, name=name, id=id)
