from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

mail = Mail()
serializer = URLSafeTimedSerializer("dummy-secret")  # 先給個假值，後面會更新
