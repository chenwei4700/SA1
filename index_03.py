from flask import Flask, request, render_template, redirect, flash, url_for, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
import mysql.connector
import re
import os
from datetime import datetime
from post_03 import post_bp


app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.register_blueprint(post_bp, url_prefix='/post')

# ✅ Gmail 寄信設定（用 Gmail 發信）
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lewalle071@gmail.com'           
app.config['MAIL_PASSWORD'] = 'bttlplcvziorqqys'        
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# ✅ 資料庫連線設定（可根據你的環境修改）
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

# ✅ 註冊路由：檢查格式＋寄信驗證
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        name = request.form['name']

        if not re.match(r'^\d{9}@m365\.fju\.edu\.tw$', account):
            flash('請使用 9 碼學號 + @m365.fju.edu.tw 註冊')
            return redirect('/register')
        if len(password) < 6:
            flash('密碼至少 6 碼')
            return redirect('/register')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE account = %s", (account,))
        if cur.fetchone():
            flash('帳號已存在')
            cur.close()
            conn.close()
            return redirect('/register')

        cur.execute("INSERT INTO Users (account, password, user_name, role, is_verified) VALUES (%s, %s, %s, 'U', 0)",
            (account, password, name))
        conn.commit()

        # ✅ 寄送驗證信
        token = serializer.dumps(account, salt='email-confirm')
        verify_url = url_for('verify_email', token=token, _external=True)
        msg = Message(subject="Email Verification",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[account])
        msg.body = f"""您好，

感謝您註冊本平台！
請點擊以下連結完成帳號驗證：

{verify_url}

此連結一小時內有效，請盡快點擊。

祝您使用愉快！
"""

        mail.send(msg)
        cur.close()
        conn.close()
        flash('註冊成功！請至信箱收驗證信完成啟用')
        return redirect('/login')

    return render_template('register.html')

# ✅ 驗證連結
@app.route('/verify/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('連結已失效或錯誤')
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET is_verified = 1 WHERE account = %s", (email,))
    conn.commit()
    cur.close()
    conn.close()
    flash('驗證成功！請登入')
    return redirect('/login')

# ✅ 登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        # 查詢使用者資料
        cur.execute("SELECT * FROM Users WHERE account = %s", (account,))
        user = cur.fetchone()

        if not user:
            flash('帳號不存在')
        elif user[2] != password:
            flash('密碼錯誤')
        elif user[5] != 1:
            flash('尚未完成信箱驗證')
        else:
            session['user'] = user[1]
            session['user_id'] = user[0]
            session['name'] = user[3]
            session['role'] = user[4]

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
        return render_template('main.html', name=session['name'], avatar=session['avatar'])
    else:
        return redirect('/')
    
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

if __name__ == '__main__':
    app.run(debug=True)
