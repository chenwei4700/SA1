from flask import Flask, render_template, request, redirect, session, flash, jsonify
import mysql.connector
import os
import re
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from post_02 import post_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# ✅ 註冊交流區 blueprint
app.register_blueprint(post_bp, url_prefix='/post')

# ✅ MySQL 資料庫連線

def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        database='SA2-2',
        unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
    )

# ✅ 上傳檔案設定
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ 首頁（登入頁）
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def do_login():
    if request.method == 'POST':
        # 只有表單送出（POST）才讀取帳號密碼
        account = request.form['account']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM Users WHERE account = %s AND password = %s", (account, password))
        user = cur.fetchone()

        if user:
            session['user'] = account                # 備用
            session['user_id'] = user[0]            # ✅ 使用 user_id 作為外鍵依據
            session['name'] = user[3]
            session['role'] = user[4]

            # ✅ 查詢最新頭像（images.user_id FK 連接 Users.user_id）
            cur.execute("""
                SELECT file_path
                FROM images
                WHERE user_id = %s
                ORDER BY uploadtime DESC
                LIMIT 1
            """, (user[0],))
            img = cur.fetchone()

            session['avatar'] = img[0] if img else 'images/avatar.png'

            cur.close()
            conn.close()
            return redirect('/dashboard')
        else:
            cur.close()
            conn.close()
            flash('登入失敗，請檢查帳號或密碼')
            return redirect('/login')
    else:
        return render_template('login.html')

# ✅ 登出
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ✅ 主頁（dashboard）
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        try:
            announcements = get_recent_announcements()  # <-- 多筆
            return render_template('main.html', 
                                   name=session['name'], 
                                   avatar=session['avatar'],
                                   announcements=announcements)  # <-- 不再用 if 判斷單筆內容
        except Exception as e:
            flash('讀取公告時發生錯誤')
            return render_template('main.html', 
                                   name=session['name'], 
                                   avatar=session['avatar'],
                                   announcements=[])
    else:
        return redirect('/')



# ✅ 註冊新帳號
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        name = request.form['name']

        if not re.match(r'^\d{9}@fju\.edu\.tw$', account):
            flash('帳號必須是9位數字+@fju.edu.tw的格式')
            return redirect('/register')

        if len(password) < 6 or len(password) > 20:
            flash('密碼長度必須在6到20字之間')
            return redirect('/register')

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM Users WHERE account = %s", (account,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()
            flash('帳號已存在，請使用其他帳號')
            return redirect('/register')

        # ✅ 插入新使用者
        cur.execute("""
            INSERT INTO Users (account, password, user_name, role)
            VALUES (%s, %s, %s, 'U')
        """, (account, password, name))
        conn.commit()

        cur.close()
        conn.close()

        flash('註冊成功！請登入')
        return redirect('/login')

    return render_template('register.html')


# ✅ 修改名字＋上傳頭像（合併版）
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user' not in session:
        return redirect('/')
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')

    if request.method == 'POST':
        new_name = request.form['name']

        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ 更新使用者名稱（使用 account 字串）
        cur.execute("UPDATE Users SET user_name = %s WHERE account = %s", (new_name, session['user']))
        conn.commit()
        session['name'] = new_name

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{session['user']}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # ✅ 插入 images（user_id 改為 FK 整數）
                cur.execute("""
                    INSERT INTO images (file_name, file_path, uploadtime, user_id)
                    VALUES (%s, %s, NOW(), %s)
                """, (filename, filepath, session['user_id']))
                conn.commit()

                session['avatar'] = filepath

        cur.close()
        conn.close()
        # flash('個人資料更新成功！')
        return redirect('/dashboard')

    return render_template('combine.html', avatar=avatar, name=name)

def get_recent_announcements():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        time_threshold = datetime.now() - timedelta(days=3)  # 過去三天
        cursor.execute("""
            SELECT * FROM Announcements 
            WHERE created_at >= %s 
              AND content IS NOT NULL 
              AND content != '' 
            ORDER BY created_at DESC
        """, (time_threshold,))
        
        announcements = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return announcements if announcements else []
    except Exception as e:
        print(f"Error fetching announcements: {e}")
        return []
    






#這裡下面是公告部分
@app.route('/announcements')
def view_all_announcements():
    if 'user' not in session:
        return redirect('/')
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM Announcements 
            WHERE content IS NOT NULL AND content != '' 
            ORDER BY created_at DESC
        """)
        
        all_announcements = cursor.fetchall()
        cursor.close()
        conn.close()
        avatar = session.get('avatar', 'images/avatar.png')
        name = session.get('name', '未登入')
        id = session.get('user_id')

        return render_template('announcements.html', announcements=all_announcements,avatar=avatar, name=name, id=id)
    except Exception as e:
        flash("無法載入公告")
        return render_template('announcements.html', announcements=[])
    
@app.route('/announcement/edit/<int:id>', methods=['PUT'])
def edit_announcement(id):
    if session.get('role') != 'M':
        return jsonify({'message': '權限不足'}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': '標題和內容皆不得為空'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE announcements SET title = %s, content = %s WHERE id = %s",
        (title, content, id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '公告已更新'})


@app.route('/announcement/delete/<int:id>', methods=['DELETE'])
def delete_announcement(id):
    if session.get('role') != 'M':
        return jsonify({'message': '權限不足'}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM announcements WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '公告已刪除'})



@app.route('/announcement/add', methods=['POST'])
def add_announcement():
    if session.get('role') != 'M':
        return jsonify({'message': '權限不足'}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': '標題與內容皆為必填'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Announcements (title, content, created_at) VALUES (%s, %s, NOW())",
        (title, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '公告已成功發布'})

if __name__ == '__main__':
    app.run(debug=True)