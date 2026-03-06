import os
from flask_mail import Message 
from app.extensions import mail 

def send_email(to, subject, body=None, html_content=None, attachment_path=None):
    try:
        msg = Message(subject, recipients=[to])
        
        if body:
            msg.body = body
            
        if html_content:
            msg.html = html_content
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as fp:
                filename = os.path.basename(attachment_path)
                
                content_type = "application/pdf" if filename.endswith('.pdf') else "text/csv"
                
                msg.attach(filename, content_type, fp.read())
                
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Mail Error: {e}")
        return False