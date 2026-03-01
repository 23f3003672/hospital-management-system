from datetime import datetime
from flask import render_template_string
from app.models import Appointment
from app.utils.mail import send_email

def send_daily_appointment_reminders(target_date):

    appointments = Appointment.query.filter(
        Appointment.appointment_date == target_date,
        Appointment.status == 'BOOKED'
    ).all()

    count = 0
    for appt in appointments:
        if not appt.patient or not appt.patient.user:
            continue

        patient_email = appt.patient.user.email
        patient_name = appt.patient.user.name
        doctor_name = appt.doctor.user.name
        time_str = appt.appointment_time.strftime("%I:%M %p")

        subject = f"Reminder: Appointment today with Dr. {doctor_name}"

        body = f"""
        Hello {patient_name},

        This is a reminder for your scheduled appointment today.

        Doctor: Dr. {doctor_name}
        Department: {appt.doctor.department.name}
        Time: {time_str}

        Kindly arrive 10 minutes early.

        Regards,
        HMS
        """

        send_email(to=patient_email, subject=subject, body=body)
        count+=1

    print(f"Sent {count} reminders for {target_date}")
    return count 
        