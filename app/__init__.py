from flask import Flask
from .extention import mail, serializer
def create_app():
    app = Flask(__name__)

    # 載入設定（可視需求）
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'lewalle071@gmail.com'           
    app.config['MAIL_PASSWORD'] = 'bttlplcvziorqqys'
    mail.init_app(app) 

    # Blueprint 或 route 模組匯入
    from .index_03 import index_bp
    from .post_02 import post_bp

    # 註冊藍圖
    app.register_blueprint(index_bp)
    app.register_blueprint(post_bp)

    return app
