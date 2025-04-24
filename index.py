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

        # 改為讀 images 資料表的最新一筆圖檔
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

        avatar = user[1] if user[1] else 'images/avatar.png'
        return render_template('main.html', name=user[0], avatar=avatar)
    else:
        return redirect('/')


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        name = request.form['name']

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
    else:
        return render_template("register.html")


@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'photo' not in request.files:
        return '沒有選擇檔案'  # ✅ return

    file = request.files['photo']
    if file.filename == '':
        return '沒有選擇檔案'  # ✅ return

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = session['user'] + '_' + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO images (file_name, file_path, uploadtime, user) VALUES (%s, %s, NOW(), %s)", 
                    (filename, filepath, session['user']))
        conn.commit()
        cur.close()
        conn.close()

        return redirect('/dashboard')  # ✅ return 成功後轉回主頁
    else:
        return '檔案格式不支援'  # ✅ return

    
@app.route('/profile')
def profile():
    if 'user' in session:
        return render_template('profile.html')
    else:
        return redirect('/')
    
@app.route('/update_name', methods=['POST'])
def update_name():
    if 'user' not in session:
        return redirect('/')
    
    new_name = request.form['name']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET user_name = %s WHERE account = %s", (new_name, session['user']))
    conn.commit()
    cur.close()
    conn.close()

    session['name'] = new_name  # 同步更新 session 裡的名字
    return redirect('/dashboard')

@app.route("/information")
def information():
    if 'user' in session:
        return render_template("information.html")
    
if __name__ == '__main__':
    app.run(debug=True)
