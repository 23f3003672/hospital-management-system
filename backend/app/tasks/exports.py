from app.extensions import celery
from app.services.reports import generate_patient_csv
from app.utils.mail import send_email
from app.models import ExportJob, User

@celery.task(bind=True, name="export_patient_csv")
def export_patient_csv(self, export_job_id):
    file_path = generate_patient_csv(export_job_id)

    job = ExportJob.query.get(export_job_id)

    if not job:
        return None 
    
    user = User.query.get(job.user_id)
    if not user:
        return None
    
    body_text = (
        "Hello,\n\n"
        "Please find your medical history CSV export attached to this email.\n\n"
        "Regards,\n"
        "HMS"
    )
    
    send_email(
        to=user.email, 
        subject="Your Medical CSV is Ready", 
        body=body_text, 
        attachment_path=file_path
    )

    return file_path