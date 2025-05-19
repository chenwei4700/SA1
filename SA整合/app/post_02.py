from flask import Blueprint, render_template, request, redirect, flash, url_for, session
import mysql.connector
from datetime import datetime
import pytz
import google.generativeai as genai#Gemini AI
post_bp = Blueprint('post', __name__)
taiwan_tz = pytz.timezone('Asia/Taipei')
GEMINI_API_KEY = "AIzaSyCvD1yTiWA3EljhiSxMLklTcniv2PVAQ_k"
genai.configure(api_key=GEMINI_API_KEY)

# ✅ 建立 MySQL 連線
def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        database='sa2-2',
        unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
    )

@post_bp.route('/post' , strict_slashes=False)
def post():
    if 'user' not in session:
        return redirect('/post')

    id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM posts WHERE user_id = %s ORDER BY created_at DESC", (id,))
    posts = cur.fetchall()
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

    conn = get_db_connection()
    cur = conn.cursor()

    # 取得所有 hashtag 給下拉選單用
    cur.execute("SELECT hashtag_id, hashtag_name FROM hashtag")
    hashtags = cur.fetchall()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        hashtag_id = request.form['hashtag']
        created_at = datetime.now(taiwan_tz)

        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        請判斷以下內容是否包含違規詞彙（如人身攻擊、霸凌、性別歧視、暴力威脅、學術不當、負面情緒等）：

        標題：{title}
        內文：{content}

        請只回傳 '違規' 或 '未違規'
        """
        
        try:
            response = model.generate_content(prompt)
            result = response.text.strip().lower()
            print(f"Gemini 回應: {result}")

            is_alert = 1 if result == '違規' else 0

            # 插入貼文
            cur.execute("""
                INSERT INTO posts (title, content, created_at, user_id, is_alert, hashtag_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, content, created_at, user_id, is_alert, hashtag_id))

            conn.commit()
            flash('貼文已成功發佈！')
            return redirect(url_for('post.interact'))

        except Exception as e:
            print(f"錯誤: {e}")
            flash("發文過程中發生錯誤，請稍後再試。")
            return redirect(url_for('post.new_post'))

        finally:
            cur.close()
            conn.close()

    return render_template('new_post.html', avatar=avatar, name=name, user_id=user_id, hashtags=hashtags)

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
        return redirect(url_for('post.post'))

    cur.execute("SELECT * FROM posts WHERE post_id = %s", (post_id,))
    post = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit_post.html', post=post, avatar=avatar, name=name)

@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))
    cur.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash('貼文已成功刪除！')
    next_page = request.form.get('next')
    if next_page == 'interact':
        return redirect(url_for('post.interact'))
    elif next_page == 'warning_post':
        return redirect(url_for('post.warning_post'))
    else:
        return redirect(url_for('post.post'))  # 預設頁面，可改為你希望的頁面

@post_bp.route('/interact')
def interact():
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 查詢所有貼文，帶出 like_count
    cur.execute("""
    SELECT 
        posts.*, 
        Users.user_name, 
        images.file_path, 
        hashtag.hashtag_name,
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count
    FROM posts
    INNER JOIN Users ON posts.user_id = Users.user_id
    LEFT JOIN (
        SELECT user_id, MAX(uploadtime) AS latest
        FROM images
        GROUP BY user_id
    ) latest_img ON latest_img.user_id = Users.user_id
    LEFT JOIN images ON images.user_id = latest_img.user_id AND images.uploadtime = latest_img.latest
    LEFT JOIN hashtag ON posts.hashtag_id = hashtag.hashtag_id
    WHERE posts.is_alert = 0
    ORDER BY posts.created_at DESC
""")
    posts = cur.fetchall()

    # 針對每篇貼文查詢留言
    for post in posts:
        cur.execute("""
            SELECT comments.*, Users.account AS author_account, Users.nickname AS author_nickname
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
    nickname = session.get('nickname')

    return render_template('interact.html', posts=posts, avatar=avatar, name=name, id=id, nickname=nickname)

@post_bp.route('/interact/search', methods=['GET', 'POST'])
def search():
    keyword = request.args.get('keyword', '').strip()
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if keyword:
        cur.execute("""
            SELECT 
                posts.*, 
                Users.user_name, 
                images.file_path, 
                hashtag.hashtag_name,
                (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count
            FROM posts
            INNER JOIN Users ON posts.user_id = Users.user_id
            LEFT JOIN (
                SELECT user_id, MAX(uploadtime) AS latest
                FROM images
                GROUP BY user_id
            ) latest_img ON latest_img.user_id = Users.user_id
            LEFT JOIN images ON images.user_id = latest_img.user_id AND images.uploadtime = latest_img.latest
            LEFT JOIN hashtag ON posts.hashtag_id = hashtag.hashtag_id
            WHERE (posts.title LIKE %s OR posts.content LIKE %s OR hashtag.hashtag_name LIKE %s)
            AND posts.is_alert = 0
            ORDER BY posts.created_at DESC
        """, (
            f"%{keyword}%", 
            f"%{keyword}%", 
            f"%{keyword}%"
        ))
        posts = cur.fetchall()
    else:
        cur.execute("""
            SELECT 
                posts.*, 
                Users.user_name, 
                images.file_path, 
                hashtag.hashtag_name,
                (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count
            FROM posts
            INNER JOIN Users ON posts.user_id = Users.user_id
            LEFT JOIN (
                SELECT user_id, MAX(uploadtime) AS latest
                FROM images
                GROUP BY user_id
            ) latest_img ON latest_img.user_id = Users.user_id
            LEFT JOIN images ON images.user_id = latest_img.user_id AND images.uploadtime = latest_img.latest
            LEFT JOIN hashtag ON posts.hashtag_id = hashtag.hashtag_id
            WHERE posts.is_alert = 0
            ORDER BY posts.created_at DESC
        """)
        posts = cur.fetchall()


    #修復posts沒有結果的問題
   
    cur.close()
    conn.close()
    
    return render_template('interact.html', posts=posts, keyword=keyword, avatar=avatar, name=name, id=id)

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

@post_bp.route('/admin/warning_post')
def warning_post():
    if 'user' not in session or session.get('role') not in ['M', 'm']:
        flash('您沒有權限訪問此頁面')
        return redirect(url_for('post.index'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # 獲取所有被標記為預警的貼文
    cur.execute("""
    SELECT posts.*, Users.user_name
    FROM posts
    JOIN Users ON posts.user_id = Users.user_id
    WHERE posts.is_alert = 1
    ORDER BY posts.created_at DESC
    """)
    
    warning_posts = cur.fetchall()
    
    cur.close()
    conn.close()

    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')

    return render_template('warning_post.html', warning_posts=warning_posts, avatar=avatar, name=name, id=id)

@post_bp.route('/post/<int:post_id>/unwarning', methods=['POST'])
def unwarning_post(post_id):
    if 'user' not in session or session.get('role') not in ['M', 'm']:
        flash('您沒有權限執行此操作')
        return redirect(url_for('post.index'))

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 更新貼文的預警狀態
        cur.execute("UPDATE posts SET is_alert = 0 WHERE post_id = %s", (post_id,))
        conn.commit()
        flash('已成功取消貼文預警')
    except Exception as e:
        print(f"錯誤: {e}")
        flash('取消預警失敗，請稍後再試')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('post.warning_post'))




#檢舉貼文

#檢舉貼文
@post_bp.route("/report/<int:post_id>", methods=["GET"])
def report_form(post_id):
    return render_template("report_form.html", post_id=post_id)
#提交檢舉
@post_bp.route("/report/<int:post_id>", methods=["POST"])
def report_post(post_id):
    if 'user' not in session:
        return redirect('/')

    reporter_id = session.get('user_id')  # 改用 reporter_id
    reason = request.form.get("reason")
    description = request.form.get("description")
    created_at = datetime.now(taiwan_tz)  # 添加時間戳記

    conn = get_db_connection()
    cur = conn.cursor()

    # 修改 SQL 語句，使用正確的欄位名稱
    cur.execute(
        "INSERT INTO reports (post_id, reporter_id, reason, created_at, status) VALUES (%s, %s, %s, %s, 'pending')",
        (post_id, reporter_id, reason, created_at)
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("檢舉已成功提交！")
    return redirect(url_for('post.interact'))

#管理者收到檢舉
@post_bp.route('/admin/flagged_posts')
def flagged_posts():
    if 'user' not in session or session.get('role') not in ['M', 'm']:
        flash('您沒有權限訪問此頁面')
        return redirect(url_for('post.post'))

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # 獲取所有被檢舉的貼文及其檢舉資訊
        cur.execute("""
            SELECT 
                p.post_id, 
                p.title, 
                p.content, 
                p.created_at,
                u.user_name as author_nickname,
                COUNT(r.report_id) as report_count
            FROM posts p
            JOIN Users u ON p.user_id = u.user_id
            JOIN reports r ON p.post_id = r.post_id
            WHERE r.status = 'pending'
            GROUP BY p.post_id, p.title, p.content, p.created_at, u.user_name
            ORDER BY report_count DESC, p.created_at DESC
        """)
        posts = cur.fetchall()

        # 為每個貼文獲取詳細的檢舉記錄
        for post in posts:
            post_id = int(post['post_id'])  # ✅ 正確在 for 裡
            cur.execute("""
            SELECT r.reason, r.created_at, u.user_name AS reporter_name
            FROM reports r
            LEFT JOIN Users u ON r.reporter_id = u.user_id
            WHERE r.post_id = %s AND r.status = 'pending'
            ORDER BY r.created_at DESC
            """, (post_id,))

            post['reports'] = cur.fetchall()

        name = session.get('name', '未登入')
        id = session.get('user_id')
        avatar = session.get('avatar', 'images/avatar.png')
        
        cur.close()
        conn.close()
        return render_template('flagged_posts.html', posts=posts, name=name, id=id, avatar=avatar)

    except Exception as e:
        print(f"錯誤類型: {type(e)}")
        print(f"錯誤: {str(e)}")
        flash('系統發生錯誤，請稍後再試')
        return redirect(url_for('post.post'))
    


@post_bp.route('/post/report', methods=['POST'])
def delete_post_and_reports():
    if 'user' not in session or session.get('role') not in ['M', 'm']:
        flash('您沒有權限執行此操作')
        return redirect(url_for('post.index'))

    post_id = request.form.get('post_id')
    if not post_id:
        flash('無效的請求，缺少貼文編號')
        return redirect(url_for('post.flagged_posts'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))
        
        # 先刪除該貼文在 reports 表的所有檢舉紀錄
        cur.execute("DELETE FROM reports WHERE post_id = %s", (post_id,))
        
        # 再刪除該貼文
        cur.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))
        
        conn.commit()
        flash('已成功刪除貼文及其相關檢舉紀錄')
    except Exception as e:
        print(f"錯誤：{e}")
        conn.rollback()
        flash('刪除失敗，請稍後再試')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('post.flagged_posts'))


#分類總覽
@post_bp.route('/admin/category_overview')
def category_overview():
    if 'user' not in session or session.get('role') not in ['M', 'm']:
        flash('您沒有權限瀏覽此頁面')
        return redirect(url_for('post.post'))

    conn = get_db_connection()
    cur = conn.cursor()

    # 抓出所有分類與其貼文數量
    cur.execute("""
        SELECT h.hashtag_name, COUNT(p.post_id) AS post_count
        FROM hashtag h
        LEFT JOIN posts p ON h.hashtag_id = p.hashtag_id
        GROUP BY h.hashtag_name
    """)
    categories = [
    {"hashtag_name": row[0], "post_count": row[1]}
    for row in cur.fetchall()]

    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')

    cur.close()
    conn.close()

    return render_template('category_overview.html', categories=categories, avatar=avatar, name=name, id=id)
#分類貼文類表
@post_bp.route('/admin/category_posts/<hashtag_name>')
def category_posts(hashtag_name):
    if 'user' not in session or session.get('role') not in ['M', 'm']:
        flash('您沒有權限瀏覽此頁面')
        return redirect(url_for('post.post'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)  # ✅ 重點改這裡

    cur.execute("""
        SELECT p.post_id, p.title, p.content, p.created_at, u.user_name
        FROM posts p
        JOIN Users u ON p.user_id = u.user_id
        JOIN hashtag h ON p.hashtag_id = h.hashtag_id
        WHERE h.hashtag_name = %s
        ORDER BY p.created_at DESC
    """, (hashtag_name,))
    
    posts = cur.fetchall()
    post_count = len(posts)
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')


    cur.close()
    conn.close()

    return render_template('category_posts.html',
                           hashtag_name=hashtag_name,
                           posts=posts,
                           post_count=post_count
                           , avatar=avatar, name=name, id=id)
#FAQ問題追蹤
@post_bp.route('/admin/faq_question')
def faq():
    if 'user' not in session or session.get('role') not in ['M', 'm']:
        flash('您沒有權限訪問此頁面')
        return redirect(url_for('post.post'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 獲取所有未回答的問題
    cur.execute("SELECT * FROM unanswer ORDER BY created_at DESC")
    questions = cur.fetchall()

    cur.close()
    conn.close()

    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    id = session.get('user_id')

    return render_template('faq_question.html', questions=questions, avatar=avatar, name=name, id=id)

#新增問題
@post_bp.route('/admin/faq_question/<int:unanswer_id>/add_answer', methods=['GET', 'POST'])
def add_answer_page(unanswer_id):
    if 'user' not in session or session.get('role') not in ['M', 'm']:
        flash('您沒有權限訪問此頁面')
        return redirect(url_for('post.post'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # 取得該問題資料
    cur.execute("SELECT * FROM unanswer WHERE unanswer_id = %s", (unanswer_id,))
    question = cur.fetchone()

    if not question:
        flash('找不到該問題')
        return redirect(url_for('post.faq'))

    if request.method == 'POST':
        answer = request.form['answer']

        # 新增至正式 FAQ 表
        cur.execute("""
            INSERT INTO faq (question, answer)
            VALUES (%s, %s)
        """, (question['unanswer_q'], answer))

        # 刪除原本未解答的問題
        cur.execute("DELETE FROM unanswer WHERE unanswer_id = %s", (unanswer_id,))
        conn.commit()
        cur.close()
        conn.close()

        flash('答案已成功新增，FAQ 已更新！')
        return redirect(url_for('post.faq'))

    cur.close()
    conn.close()
    return render_template('add_answer.html', question=question)
