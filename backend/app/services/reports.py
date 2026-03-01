import csv
import os
from datetime import date, timedelta, datetime
from app.models import Doctor, Appointment, ExportJob, Patient 

from app.extensions import db, mail
from flask_mail import Message
from app.utils.reports import build_doctor_report_html

def generate_patient_csv(job_id):
    job = ExportJob.query.get(job_id)
    if not job:
        return None
    patient = Patient.query.filter_by(user_id=job.user_id).first()
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc()).all()

    filename = f"patient_{job.user_id}_history_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
    filepath = os.path.join("exports", filename)
    os.makedirs("exports", exist_ok=True)

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(["Date", "Time", "Doctor", "Department", "Diagnosis", "Prescription", "Notes"])

        for appt in appointments:
            doctor_name = appt.doctor.user.name if appt.doctor else "Unknown"
            dept_name = appt.doctor.department.name if appt.doctor else "Unknown"

            diagnosis = appt.treatment.diagnosis if appt.treatment else "N/A"
            prescription = appt.treatment.prescription if appt.treatment else "N/A"
            notes = appt.treatment.notes if appt.treatment else "N/A"

            writer.writerow([
                appt.appointment_date.isoformat(),
                appt.appointment_time.strftime("%H:%M"),
                doctor_name,
                dept_name,
                diagnosis,
                prescription,
                notes 
            ])
    job.status = "COMPLETED"
    job.file_path = filepath
    job.completed_at = datetime.utcnow()
    db.session.commit()

    return filepath

def generate_and_send_monthly_doctor_reports():

    #original logic
    #today = date.today()
    #first = today.replace(day=1)
    #last_month = first - timedelta(days=1)
    #start_date = last_month.replace(day=1)
    #end_date = last_month

    #logic for testing for current month
    today = date.today()
    start_date = today.replace(day=1)
    end_date = today


    
    print(f"Generating reports for period: {start_date} to {end_date}")

    doctors = Doctor.query.filter_by(is_active=True).all()
    count = 0

    for doc in doctors:
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).all()

        if not appointments:
            continue 

        html_body = build_doctor_report_html(doc, appointments,treatments=None, start_date=start_date, end_date=end_date)

        try:
            msg = Message(
                subject = f"Monthly Activity Report - {start_date.strftime('%B %Y')}",
                recipients=[doc.user.email],
                html=html_body
            )
            mail.send(msg)
            count += 1
            print(f"Report sent to {doc.user.email}")

        except Exception as e:
            print(f"Failed to send report to {doc.user.email}: {e}")
            
    return count
