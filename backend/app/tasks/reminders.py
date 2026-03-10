from app.extensions import celery
from datetime import date
from app.services.notifications import send_daily_appointment_reminders

@celery.task(bind=True, name="daily_appointment_reminders")
def daily_appointment_reminders(self):
    target_date = date.today()
    count = send_daily_appointment_reminders(target_date)
    return f"Reminders sent for {count} appointments"