def build_doctor_report_html(doctor, appointments, treatments=None, start_date=None, end_date=None):

    if isinstance(treatments, (str, type(None))) and hasattr(treatments, 'strftime'):
        end_date = start_date
        start_date = treatments
        treatments = []

    treatments = treatments or []
    start_str = start_date.strftime('%Y-%m-%d') if start_date else "Unknown"
    end_str = end_date.strftime('%Y-%m-%d') if end_date else "Unknown"

    na_span = "<span style='color: #94a3b8;'>N/A</span>"
    none_span = "<span style='color: #94a3b8;'>None</span>"

    rows = []
    for a in appointments[:20]:
        patient_name = a.patient.user.name if a.patient and a.patient.user else "Unknown"
        diagnosis = a.treatment.diagnosis if a.treatment else na_span
        tests = a.treatment.tests_done if a.treatment and a.treatment.tests_done else none_span
        prescription = a.treatment.prescription if a.treatment else na_span
        
        notes = a.treatment.notes if a.treatment and a.treatment.notes else ""
        notes_html = f"<br><small style='color: #64748b;'>{notes}</small>" if notes else ""

        row = (
            f"<tr>"
            f"<td style='border: 1px solid #cbd5e1; padding: 8px;'>{a.appointment_date}<br><small style='color: #64748b;'>{a.appointment_time}</small></td>"
            f"<td style='border: 1px solid #cbd5e1; padding: 8px;'>{patient_name}</td>"
            f"<td style='border: 1px solid #cbd5e1; padding: 8px;'><strong>{a.status}</strong></td>"
            f"<td style='border: 1px solid #cbd5e1; padding: 8px;'>{diagnosis}</td>"
            f"<td style='border: 1px solid #cbd5e1; padding: 8px;'>{tests}</td>"
            f"<td style='border: 1px solid #cbd5e1; padding: 8px;'>{prescription}{notes_html}</td>"
            f"</tr>"
        )
        rows.append(row)
        
    rows_html = "".join(rows)
    limit_notice = "<p style='color: #64748b;'><em>(Showing last 20 records)</em></p>" if len(appointments) > 20 else ""

    return f"""
    <html>
    <body style="font-family:Arial, sans-serif;">
        <h2 style="color: #0f766e;">Clinical Activity Report</h2>
        <p><strong>Doctor:</strong> Dr. {doctor.user.name}</p>
        <p><strong>Period:</strong> {start_str} to {end_str}</p>

        <hr style="border: 0; height: 1px; background: #ddd; margin-bottom: 20px;">
        
        <h3 style="color: #334155;">Summary</h3>
        <ul>
            <li><strong>Total Appointments:</strong> {len(appointments)}</li>
            <li><strong>Total Treatments Recorded:</strong> {len(treatments)}</li>
        </ul>

        <h3 style="color: #334155;">Detailed Appointment Log</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr style="background-color: #f8fafc; color: #334155;">
                <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">Date & Time</th>
                <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">Patient Name</th>
                <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">Status</th>
                <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">Diagnosis</th>
                <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">Tests Done</th>
                <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">Prescription & Notes</th>
            </tr>
            {rows_html}
        </table>
        {limit_notice}
        
        <br>
        <p style="color: #94a3b8; font-size:12px; text-align: center; margin-top: 30px;"> Generated securely by HMS </p>
    </body>
    </html>
    """