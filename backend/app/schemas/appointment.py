def appointment_basic_schema(appt):
    return{
        "id": appt.id,
        "doctor":{
            "id": appt.doctor.id,
            "email": appt.doctor.user.email,
            "department": appt.doctor.department.name if appt.doctor.department else "Unassigned"
        },

        "patient": {
            "id": appt.patient.id,
            "email": appt.patient.user.email
        },

        "date": appt.appointment_date.isoformat(),
        "time": appt.appointment_time.strftime("%H:%M"),
        "status": appt.status,
    }

def serialize_appointment_history(appt):
    return {
        "id": appt.id,
        "appointment_id": appt.id, 
        "date": appt.appointment_date.isoformat(),
        "time": appt.appointment_time.strftime("%I:%M %p"), 
        "status": appt.status,
        
        "doctor_name": appt.doctor.user.name if appt.doctor else "Unknown Doctor",
        "patient_name": appt.patient.user.name if appt.patient else "Unknown Patient",
        "doctor": {
            "id": appt.doctor.id, 
            "name": appt.doctor.user.name, 
            "department": appt.doctor.department.name if appt.doctor.department else "General"
        } if appt.doctor else None,
        "patient": {
            "id": appt.patient.id, 
            "name": appt.patient.user.name
        } if appt.patient else None,

        "diagnosis": appt.treatment.diagnosis if appt.treatment else None,
        "prescription": appt.treatment.prescription if appt.treatment else None,
        "notes": appt.treatment.notes if appt.treatment else None,
        "visit_type": appt.treatment.visit_type if appt.treatment else None,
        "tests_done": appt.treatment.tests_done if appt.treatment else None,
    }