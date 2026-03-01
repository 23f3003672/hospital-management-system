from flask import Blueprint, jsonify, request 
from flask_security import login_required, roles_required
from flask_security.utils import hash_password
from sqlalchemy import func, or_ 
from sqlalchemy.exc import IntegrityError
from app.extensions import db 
from app.models import Doctor, Patient, Appointment, User , Role, Department, Treatment
from app.schemas.appointment import serialize_appointment_history
from app.utils.cache import cache_delete, build_cache_key, cache_get, cache_set
from app.config import Config
from uuid import uuid4 
from app.tasks.reminders import daily_appointment_reminders
from app.tasks.reports import monthly_doctor_reports

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
SHORT_TTL = Config.SHORT_TTL

@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@roles_required("admin")
def admin_dashboard_counts():
    return jsonify({
        "total_doctors": Doctor.query.count(),
        "total_patients": Patient.query.count(),
        "total_appointments": Appointment.query.count()
    }), 200

#Department Management Routes
@admin_bp.route("/departments", methods=["GET","POST"])
@login_required
@roles_required("admin")
def manage_departments():
    if request.method == "POST":
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Department name is required"}), 400
        
        if Department.query.filter(Department.name.ilike(data["name"])).first():
            return jsonify({"error": "Department already exists"}), 400
        
        dept = Department(name=data["name"], description=data.get("description", ""))
        db.session.add(dept)
        db.session.commit()
        return jsonify({"message":"Department added", "id": dept.id, "name": dept.name}), 201
    
    depts = Department.query.all()
    return jsonify([{"id": d.id, "name": d.name} for d in depts]), 200

@admin_bp.route("/departments/<int:id>", methods=["DELETE"])
@login_required
@roles_required("admin")
def delete_department(id):
    dept = Department.query.get_or_404(id)
    try:
        db.session.delete(dept)
        db.session.commit()
        return jsonify({"message":"Department deleted"}), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete department.It has doctors assigned."}), 400



#DOCTOR MANAGEMENT ROUTES
@admin_bp.route("/doctors", methods=["POST"])
@login_required
@roles_required("admin")
def add_doctor():
    data = request.get_json()
    required = ["email", "password", "name", "department_id"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    doctor_role = Role.query.filter_by(name="doctor").first()
    if not doctor_role:
        return jsonify({"error": "Doctor role not found"}), 500
    
    try:
        #creating the user
        user = User(name=data["name"], email=data["email"], password = hash_password(data["password"]),fs_uniquifier=str(uuid4()), active = True)

        user.roles.append(doctor_role)
        db.session.add(user)
        db.session.flush()

        #creating the doctor profile
        doctor = Doctor(user_id = user.id, department_id = data["department_id"], experience = data.get("experience", 0), qualification = data.get("qualification", ""), description = data.get("description", ""), is_active = True)

        db.session.add(doctor)
        db.session.commit()

        cache_delete(build_cache_key("patient_doctors", "all"))
        return jsonify({"message": "Doctor created successfully", "doctor_id":doctor.id}), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Doctor with this email id already exists"}), 409
    

@admin_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
@login_required
@roles_required("admin")
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()

    if "name" in data:
        doctor.user.name = data["name"]
    
    if "department_id" in data:
        doctor.department_id = data["department_id"]
    if "experience" in data:
        doctor.experience = data["experience"]

    if "qualification" in data:
        doctor.qualification = data["qualification"]
    if "description" in data:
        doctor.description = data["description"]

    if "is_active" in data:
        doctor.is_active = bool(data["is_active"])

    try:
        db.session.commit()    
        cache_delete(build_cache_key("patient_doctors", "all"))
        return jsonify({"message": "Doctor updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@admin_bp.route("/doctor/<int:doctor_id>", methods=["DELETE"])
@login_required
@roles_required("admin")
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user

    try:
        db.session.delete(doctor)
        db.session.delete(user)
        db.session.commit()
        cache_delete(build_cache_key("patient_doctors", "all"))
        return jsonify({"message":"Doctor deleted successfully"}), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete doctor.They have existing appointments."}), 400


@admin_bp.route("/doctors/search", methods=["GET"])
@login_required
@roles_required("admin")
def search_doctors():
    name = request.args.get("name", "").strip()
    query = Doctor.query.join(User).join(Department)
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    doctors = query.all()
    return jsonify([{
        "doctor_id": d.id,
        "name": d.user.name,
        "email": d.user.email,
        "department": d.department.name,
        "experience": d.experience,
        "qualification": d.qualification,
        "description": d.description,
        "is_active": d.is_active,
    } for d in doctors]), 200 


#PATIENT MANAGEMENT ROUTES

@admin_bp.route("/patients/<int:patient_id>", methods=["PUT"])
@login_required
@roles_required("admin")
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()

    if "is_active" in data:
        patient.is_active = bool(data["is_active"])

    if "name" in data and data["name"]:
        patient.user.name = data["name"]
    
    if "email" in data and data["email"]:
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != patient.user.id:
            return jsonify({"error": "Email already in use"}), 409
        patient.user.email = data["email"]

    try:
        db.session.commit()    
        return jsonify({"message": "Patient updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@admin_bp.route("/patients/<int:patient_id>", methods=["DELETE"])
@login_required
@roles_required("admin")
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    user = patient.user

    try:
        db.session.delete(patient)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message":"Patient deleted successfully"}), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete patient.They have existing appointments."}), 400


@admin_bp.route("/patients/search", methods=["GET"])
@login_required
@roles_required("admin")
def search_patients():
    name = request.args.get("name", "").strip()
    
    cache_key = build_cache_key("patient_search", name if name else "all")
    cached_data = cache_get(cache_key)
    if cached_data:
        return jsonify(cached_data), 200

    query = Patient.query.join(User)
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    patients = query.all()
    result_data = [{
        "patient_id": p.id,
        "name": p.user.name,
        "email": p.user.email,
        "is_active": p.is_active,
    } for p in patients]

    cache_set(cache_key, result_data, ttl=SHORT_TTL)

    return jsonify(result_data), 200

#APPOINTMENT MANAGEMENT ROUTES 

@admin_bp.route("/appointments", methods=["GET"])
@login_required
@roles_required("admin")
def view_all_appointments():
    query = Appointment.query 
    if request.args.get("status"):
        query = query.filter(Appointment.status == request.args["status"])

    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify([{
        "appointment_id": a.id,
        "date": a.appointment_date.isoformat(),
        "time": a.appointment_time.strftime("%H:%M"),
        "status": a.status,
        "doctor": {"id": a.doctor.id, "name": a.doctor.user.name},
        "patient": {"id": a.patient.id, "name": a.patient.user.name},
    } for a in appointments]), 200

@admin_bp.route("/appointments/history", methods=["GET"])
@login_required
@roles_required("admin")
def get_all_appointment_history():
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify({"count": len(appointments), "appointments" : [serialize_appointment_history(a) for a in appointments]}),200

@admin_bp.route("/trigger-reminders", methods=["POST"])
@login_required
@roles_required("admin")
def trigger_reminders():
    task = daily_appointment_reminders.delay()
    return jsonify({"message": "Daily reminders triggered", "task_id": task.id}), 200

@admin_bp.route("/trigger-reports", methods=["POST"])
@login_required
@roles_required("admin")
def trigger_reports():
    task = monthly_doctor_reports.delay()
    return jsonify({"message": "Monthly reports triggered","task_id": task.id}), 200


