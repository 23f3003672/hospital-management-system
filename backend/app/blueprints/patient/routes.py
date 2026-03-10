from datetime import date, timedelta, datetime
from flask import Blueprint, request, jsonify
from flask_security import login_required, roles_required, current_user, roles_accepted
from flask_security.utils import hash_password
from app.services.booking import book_appointment, reschedule_appointment, validate_status_transition, BookingError, DoctorNotFoundError, SlotAlreadyBookedError, OutsideAvailabilityError, PastAppointmentError, PatientOverlapError, InvalidAppointmentStateError, UnauthorizedAppointmentAccessError
from app.schemas.patient import department_schema, doctor_schema
from app.models import Department, Doctor, DoctorAvailability, Appointment, ExportJob
from app.schemas.appointment import appointment_basic_schema, serialize_appointment_history
from app.utils.constants import APPOINTMENT_STATUS_CANCELLED, APPOINTMENT_STATUS_BOOKED
from app.extensions import db
from app.tasks.exports import export_patient_csv
from app.utils.cache import cache_delete, cache_get, cache_set, build_cache_key, LONG_TTL, MEDIUM_TTL

patient_bp = Blueprint("patient", __name__, url_prefix="/api/patient")

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None
    
def parse_time(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except Exception:
        return None

def get_current_patient_id():
    if not hasattr( current_user, 'patient') or not current_user.patient:
        return None
    return current_user.patient.id

#PATIENT PROFILE ROUTES

@patient_bp.route("/me", methods=["GET"])
@login_required
@roles_required("patient")
def get_patient_profile():
    return jsonify({
        "name": current_user.name,
        "email": current_user.email,
        "id": current_user.id,
        "phone": current_user.patient.phone if current_user.patient else "",
        "address": current_user.patient.address if current_user.patient else ""
    })

@patient_bp.route("/me", methods=["PUT"])
@login_required
@roles_required("patient")
def update_profile():
    data = request.get_json()
    user = current_user
    patient = user.patient

    if "name" in data and data["name"]:
        user.name = data["name"]

    if "password" in data and data["password"]:
        if len(data["password"]) < 6:
            return jsonify({"error":"Password must be at least 6 characters"}), 400
        user.password = hash_password(data["password"])

    if patient:
        if "phone" in data:
            patient.phone = data["phone"]
        if "address" in data:
            patient.address = data["address"]
    
    try:
        db.session.commit()
        return jsonify({"message":"Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":"Failed to update profile"}), 500


#APPOINTMENT ROUTES
@patient_bp.route("/appointments", methods=["POST"])
@login_required
@roles_required("patient")
def create_appointment():
    pid = get_current_patient_id()
    if not pid:
        return jsonify({"error":"Patient profile not found.Please contact HMS admin."}), 404
    
    data = request.get_json() or {}
    doctor_id = data.get("doctor_id")
    appointment_date = parse_date(data.get("date"))
    appointment_time = parse_time(data.get("time_slot"))

    if not all([doctor_id, appointment_date, appointment_time]):
        return jsonify({"error":"Invalid request data"}), 400
    
    now = datetime.now()
    if appointment_date < now.date() or (appointment_date == now.date() and appointment_time < now.time()):
        return jsonify({"error": "Cannot book a slot that has already passed."}), 400
    
    try:
        appt = book_appointment(
            patient_id = pid,
            doctor_id = doctor_id,
            appointment_date = appointment_date,
            appointment_time = appointment_time,
        )
        cache_delete(build_cache_key("patient_appointments", current_user.id))
        return jsonify({"message":"Appointment booked successfully", "appointment_id":appt.id}), 201
    except (DoctorNotFoundError, SlotAlreadyBookedError, PatientOverlapError, OutsideAvailabilityError, PastAppointmentError, BookingError) as e:
        return jsonify({"error": str(e)}), 400
    
@patient_bp.route("/appointments/<int:appointment_id>/reschedule", methods=["PUT"])
@login_required
@roles_required("patient")
def reschedule(appointment_id):
    pid = get_current_patient_id()
    data = request.get_json() or {}
    new_date = parse_date(data.get("date"))
    new_time = parse_time(data.get("time"))

    if not all([new_date, new_time]):
        return jsonify({"error":"Invalid request"}), 400
    
    try:
        reschedule_appointment(appointment_id=appointment_id, patient_id=pid, new_date=new_date, new_time=new_time)
        return jsonify({"message": "Appointment rescheduled successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@patient_bp.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
@login_required
@roles_required("patient")
def cancel(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    try:
        validate_status_transition(appointment, APPOINTMENT_STATUS_CANCELLED, actor_role="patient")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    appointment.status = APPOINTMENT_STATUS_CANCELLED
    db.session.commit()
    return jsonify({"message":"Appointment cancelled successfully."}), 200


@patient_bp.route("/appointments/upcoming", methods=["GET"])
@login_required
@roles_required("patient")
def upcoming_appointments():
    pid = get_current_patient_id()
    if not pid:
        return jsonify([]), 200
    
    today = date.today()

    appointments = Appointment.query.filter(
        Appointment.patient_id == pid,
        Appointment.appointment_date >= today,
        Appointment.status == APPOINTMENT_STATUS_BOOKED
    ).order_by(Appointment.appointment_date).all()

    result = []
    for a in appointments:
        result.append({
            "id": a.id,
            "date": a.appointment_date.isoformat(),
            "time": a.appointment_time.strftime("%I:%M %p"), 
            
            "doctor_name": a.doctor.user.name if a.doctor and a.doctor.user else "Unknown",
            "department_name": a.doctor.department.name if a.doctor and a.doctor.department else "General Medicine"
        })

    return jsonify(result), 200


@patient_bp.route("/appointments/history", methods=["GET"])
@login_required
@roles_required("patient")
def appointment_history():
    pid = get_current_patient_id()
    if not pid:
        return jsonify({"count":0, "appointments":[]}), 200
    
    appointments = Appointment.query.filter(Appointment.patient_id == pid).order_by(Appointment.appointment_date.desc()).all()
    return jsonify({
        "count":len(appointments),
        "appointments": [serialize_appointment_history(a) for a in appointments]
    }), 200

@patient_bp.route("/departments", methods=["GET"])
@login_required
@roles_accepted("patient", "admin")
def get_department():
    cache_key = build_cache_key("departments", "all")
    cached_data = cache_get(cache_key)
    if cached_data:
        return jsonify(cached_data), 200
    
    departments = Department.query.all()
    department_data = [department_schema(d) for d in departments]
    cache_set(cache_key, department_data, ttl=LONG_TTL)
    return jsonify(department_data), 200


@patient_bp.route("/departments/<int:id>", methods=["GET"])
@login_required
@roles_required("patient")
def get_single_department(id):
    dept = Department.query.get_or_404(id)
    return jsonify({
        "id": dept.id,
        "name": dept.name,
        "description": dept.description
    }), 200


@patient_bp.route("/doctors", methods=["GET"])
@login_required
@roles_required("patient")
def get_doctors():
    department_id = request.args.get("department_id")
    search = request.args.get("search", "").strip()

    cache_key = build_cache_key("patient_doctors", department_id or "all", search or "all")
    cached_data = cache_get(cache_key)
    if cached_data:
        return jsonify(cached_data), 200
    
    query = Doctor.query.filter_by(is_active=True)

    if department_id:
        query = query.filter_by(department_id=department_id)

    if search:
        query = query.join(Doctor.user).filter(Doctor.user.name.ilike(f"%{search}%"))

    doctors = query.all()
    doctor_data = []
    for d in doctors:
        doctor_data.append({
            "id": d.id,
            "name": d.user.name,
            "email": d.user.email,
            "department_name": d.department.name if d.department else "General Medicine",
            "qualification": d.qualification or "MBBS",
            "experience": d.experience or 0
        })
    cache_set(cache_key, doctor_data, ttl=MEDIUM_TTL)
    return jsonify(doctor_data), 200


@patient_bp.route("/doctors/<int:doctor_id>/availability", methods=["GET"])
@login_required
@roles_required("patient")
def doctor_availability(doctor_id):
    now = datetime.now()
    today = now.date()
    current_time = now.time()
    
    end_date = today + timedelta(days=7)
    records = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.available_date >= today,
        DoctorAvailability.available_date <= end_date
    ).order_by(DoctorAvailability.available_date).all()

    slots_data = []
    for r in records:
        is_past = False
        if r.available_date < today or (r.available_date == today and r.start_time < current_time):
            is_past = True

        conflict = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=r.available_date,
            appointment_time=r.start_time,
            status=APPOINTMENT_STATUS_BOOKED
        ).first()
        is_booked = conflict is not None

        slots_data.append({
            "date": r.available_date.isoformat(),
            "start_time": r.start_time.strftime("%H:%M"),
            "end_time": r.end_time.strftime("%H:%M"),
            "is_past": is_past,
            "is_booked": is_booked,
            "status": "past" if is_past else ("booked" if is_booked else "available")
        })

    return jsonify(slots_data), 200

@patient_bp.route("/export-csv", methods=["POST"])
@login_required
@roles_required("patient")
def export_csv():
    job = ExportJob(user_id = current_user.id, job_type = "treatment_csv", status="PENDING")
    db.session.add(job)
    db.session.commit()
    export_patient_csv.delay(job.id)
    return jsonify({"message":"Your csv is being prepared."}), 202