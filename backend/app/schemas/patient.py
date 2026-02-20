def patient_profile_schema(patient):
    return {
        "id": patient.id,
        "email": patient.user.email,
        "name": patient.user.name,
        "phone": patient.phone,
        "address": patient.address,
        "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        "is_active": patient.is_active
    }

def department_schema(department):
    return {
        "id": department.id,
        "name": department.name,
        "description": department.description,
    }

def doctor_schema(doctor):
    return {
        "id": doctor.id,
        "name": doctor.user.name,
        "email": doctor.user.email,
        "department": doctor.department.name,
        "qualification": doctor.qualification,
        "experience": doctor.experience,
        "is_active": doctor.is_active
    }