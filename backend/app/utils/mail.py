import os
from flask_mail import Message 
from app.extensions import mail 

def send_email(to, subject, body, attachment_path=None):
    try:
        msg = Message(subject, recipients=[to])
        msg.body = body
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as fp:
                filename = os.path.basename(attachment_path)
                msg.attach(filename, "text/csv", fp.read())
                
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Mail Error: {e}")
        return False