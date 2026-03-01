from app.extensions import celery
from app.services.reports import generate_and_send_monthly_doctor_reports

@celery.task(bind=True, name="monthly_doctor_reports")
def monthly_doctor_reports(self):
    count = generate_and_send_monthly_doctor_reports()
    return f"Monthly reports sent to {count} doctors"