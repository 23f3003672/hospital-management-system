from celery.schedules import crontab 
from celery_worker import celery_app

celery_app.conf.beat_schedule = {
    "daily-appointment-reminders": {
        "task": "daily_appointment_reminders",
        "schedule": crontab(hour=9, minute=0)
    },
    "monthly-doctor-reports": {
        "task": "monthly_doctor_reports",
        "schedule": crontab(day_of_month=1, hour=0, minute=5),
    },
}