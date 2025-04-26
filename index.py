from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ✅ 建立資料庫連線
def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        database='sa_goal2',
        unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
    )

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 最大2MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ 除錯用：印出目前連到的資料庫清單
try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SHOW DATABASES;")
    print("✅ Flask 成功連線，目前看到的資料庫清單：")
    for db in cur.fetchall():
        print(" -", db[0])
    cur.close()
    conn.close()
except Exception as e:
    print("❌ Flask 連不到資料庫：", e)


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def do_login():
    account = request.form['account']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE account = %s AND password = %s", (account, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        session['user'] = account
        session['name'] = user[3]  # user_name 第四欄
        return redirect('/dashboard')
    else:
        return "登入失敗，請檢查帳號密碼"


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        conn = get_db_connection()
        cur = conn.cursor()

        # 讀取用戶的名字和最新一筆圖檔
        cur.execute(""" 
            SELECT u.user_name, i.file_path
            FROM Users u
            LEFT JOIN images i ON u.account = i.user
            WHERE u.account = %s
            ORDER BY i.uploadtime DESC
            LIMIT 1
        """, (session['user'],))

        user = cur.fetchone()
        cur.close()
        conn.close()

        # 頭像的路徑處理
        avatar = user[1] if user[1] else 'images/avatar.png'  # 默認的 avatar
        return render_template('main.html', name=user[0], avatar=avatar)
    else:
        return redirect('/')
