from app.models import Appointment
from app.utils.mail import send_email
from app.utils.constants import APPOINTMENT_STATUS_BOOKED

def send_daily_appointment_reminders(target_date):

    appointments = Appointment.query.filter(
        Appointment.appointment_date == target_date,
        Appointment.status == APPOINTMENT_STATUS_BOOKED
    ).all()

    count = 0
    for appt in appointments:
        if not appt.patient or not appt.patient.user:
            continue

        patient_email = appt.patient.user.email
        patient_name = appt.patient.user.name
        doctor_name = appt.doctor.user.name
        department_name = appt.doctor.department.name
        time_str = appt.appointment_time.strftime("%I:%M %p")

        subject = f"Reminder: Your Appointment Today with Dr. {doctor_name}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f8fafc;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8fafc; padding: 40px 0;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); overflow: hidden; border: 1px solid #e2e8f0;">
                            
                            <tr>
                                <td style="background-color: #0f766e; padding: 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; letter-spacing: -1px;">HMS</h1>
                                    <p style="color: #ccfbf1; margin: 5px 0 0 0; font-size: 14px;">Hospital Management System</p>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #334155; margin-top: 0; font-size: 20px;">Hello {patient_name},</h2>
                                    <p style="color: #475569; font-size: 16px; line-height: 1.5;">
                                        This is a friendly reminder for your scheduled appointment today. We look forward to seeing you.
                                    </p>
                                    
                                    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; border-radius: 6px; margin: 25px 0;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <p style="margin: 0 0 10px 0; font-size: 16px; color: #334155;"><strong>Doctor:</strong> Dr. {doctor_name}</p>
                                                <p style="margin: 0 0 10px 0; font-size: 16px; color: #334155;"><strong>Department:</strong> {department_name}</p>
                                                <p style="margin: 0; font-size: 16px; color: #334155;"><strong>Time:</strong> <span style="color: #0f766e; font-weight: bold;">{time_str}</span></p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="color: #475569; font-size: 15px; margin-top: 25px;">
                                        <em>Kindly arrive 10 minutes early to complete any necessary check-in procedures.</em>
                                    </p>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                                    <p style="color: #64748b; font-size: 12px; margin: 0;">
                                        This is an automated message generated securely by HMS. Please do not reply to this email.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        send_email(to=patient_email, subject=subject, html_content=html_content)
        count += 1

    print(f"Sent {count} reminders for {target_date}")
    return count