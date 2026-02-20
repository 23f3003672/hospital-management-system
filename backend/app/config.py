import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:

    SECRET_KEY = "dev-secret-key"
    SECURITY_PASSWORD_SALT = "dev-password-salt"

    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_LENGTH_MIN = 8

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "../hms.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECURITY_REGISTERABLE = False 
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = False
    SECURITY_TRACKABLE = False

    SESSION_COOKIE_NAME = "hms_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    REMEMBER_COOKIE_HTTPONLY =True
    REMEMBER_COOKIE_SAMESITE = "Lax"

    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_SUPPRESS_SEND = False 
    MAIL_DEFAULT_SENDER = "hms@localhost"

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0

    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TASK_SERIALIZER = "json"
    TIMEZONE = "Asia/Kolkata"

    SHORT_TTL = 300
    MEDIUM_TTL = 600
    LONG_TTL = 3600

    WTF_CSRF_ENABLED = False 
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True 