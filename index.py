from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import os
import re
from werkzeug.utils import secure_filename
from datetime import datetime
from post import post_bp, db

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ✅ SQLite 設定給交流區用
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ 初始化資料庫
db.init_app(app)
with app.app_context():
    db.create_all()

# ✅ 註冊交流區 blueprint
app.register_blueprint(post_bp, url_prefix='/post')

# ✅ MySQL 資料庫連線

def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        database='sa_goal2',
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

# ✅ 登入功能
@app.route('/login', methods=['POST'])
def do_login():
    account = request.form['account']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Users WHERE account = %s AND password = %s", (account, password))
    user = cur.fetchone()

    if user:
        session['user'] = account
        session['name'] = user[3]
        session['role'] = user[4]

        # 查詢頭像
        cur.execute("""
            SELECT file_path
            FROM images
            WHERE user = %s
            ORDER BY uploadtime DESC
            LIMIT 1
        """, (account,))
        img = cur.fetchone()

        if img and img[0]:
            session['avatar'] = img[0]
        else:
            session['avatar'] = 'images/avatar.png'

        cur.close()
        conn.close()

        return redirect('/dashboard')

    else:
        cur.close()
        conn.close()
        return "登入失敗，請檢查帳號密碼"

# ✅ 登出
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ✅ 主頁（dashboard）
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('main.html', name=session['name'], avatar=session['avatar'])
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
            return "帳號必須是9位數字+@fju.edu.tw的格式"
        # ✅ 檢查密碼長度
        if len(password) < 6 or len(password) > 20:
            return "密碼長度必須在6到20字之間"
        
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM Users WHERE account = %s", (account,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()
            return "帳號已存在，請使用其他帳號"

        cur.execute("INSERT INTO Users (account, password, user_name, role) VALUES (%s, %s, %s, 'U')", (account, password, name))
        conn.commit()
        cur.close()
        conn.close()

        return redirect('/')

    return render_template('register.html')

# ✅ 修改名字＋上傳頭像（合併版）
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    avatar = session.get('avatar', 'images/avatar.png')
    name = session.get('name', '未登入')
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        new_name = request.form['name']

        conn = get_db_connection()
        cur = conn.cursor()

        # 更新名字
        cur.execute("UPDATE Users SET user_name = %s WHERE account = %s", (new_name, session['user']))
        conn.commit()
        session['name'] = new_name

        # 更新頭像（如果有選）
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = session['user'] + '_' + filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                cur.execute("INSERT INTO images (file_name, file_path, uploadtime, user) VALUES (%s, %s, NOW(), %s)",
                            (filename, filepath, session['user']))
                conn.commit()
                session['avatar'] = filepath

        cur.close()
        conn.close()

        flash('個人資料更新成功！')
        return redirect('/dashboard')

    return render_template('combine.html', avatar=avatar, name=name)


if __name__ == '__main__':
    app.run(debug=True)
