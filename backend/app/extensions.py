from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore 
from flask_mail import Mail 
from celery import Celery 
from redis import Redis 

mail = Mail()
db = SQLAlchemy()
security = Security()
redis_client = None 

celery = Celery(__name__)
user_datastore = None 

def init_extensions(app):
    global redis_client, user_datastore

    db.init_app(app)
    mail.init_app(app)

    from app.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app,user_datastore)

    redis_client = Redis(host=app.config["REDIS_HOST"],
                         port = app.config["REDIS_PORT"],
                         db = app.config["REDIS_DB"],
                         decode_responses=True)
    
    celery.conf.update( broker_url = app.config["CELERY_BROKER_URL"], result_backend = app.config["CELERY_RESULT_BACKEND"], timezone = app.config["TIMEZONE"], accept_content = app.config["CELERY_ACCEPT_CONTENT"], task_serializer = app.config["CELERY_TASK_SERIALIZER"],)