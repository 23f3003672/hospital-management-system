from flask import Blueprint, jsonify, request
from flask_security import login_required, roles_required, current_user
from app.models import Doctor, Appointment, DoctorAvailability, Treatment, Patient 
from app.extensions import db
from datetime import date, timedelta, datetime
from app.schemas.appointment import serialize_appointment_history
from app.services.booking import validate_status_transition
from app.utils.constants import APPOINTMENT_STATUS_COMPLETED, APPOINTMENT_STATUS_CANCELLED
from app.utils.cache import cache_get, cache_delete, cache_set, build_cache_key, SHORT_TTL

doctor_bp = Blueprint("doctor", __name__, url_prefix="/api/doctor")

def get_current_doctor():
    return Doctor.query.filter_by(user_id = current_user.id).first()

@doctor_bp.route("/me", methods=["GET"])
@login_required
@roles_required("doctor")
def doctor_me():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404
    
    return jsonify({
        "doctor_id": doctor.id,
        "name": doctor.user.name,
        "email":doctor.user.email,
        "department": doctor.department.name
    }), 200



#APPOINTMENT ROUTES
@doctor_bp.route("/appointments", methods=["GET"])
@login_required
@roles_required("doctor")
def view_appointments():
    view = request.args.get("view")
    if view not in ("day", "week"):
        return jsonify({"error": "Invalid view"}), 400
    
    doctor = get_current_doctor()
    today = date.today()
    query = Appointment.query.filter(Appointment.doctor_id == doctor.id)

    if view == "day":
        query = query.filter(Appointment.appointment_date == today)

    else:
        end_date = today + timedelta(days=7)
        query = query.filter(Appointment.appointment_date >= today, Appointment.appointment_date <= end_date)

    appointments = query.order_by(Appointment.appointment_date, Appointment.appointment_time).all()

    return jsonify({
        "appointments": [
            {
                "appointment_id": a.id,
                "date": a.appointment_date.isoformat(),
                "time": a.appointment_time.strftime("%H:%M"),
                "status": a.status,
                "patient": {"id": a.patient.id, "name": a.patient.user.name}
            }
            for a in appointments
        ]
    }), 200


#AVAILABILITY ROUTES
@doctor_bp.route("/availability", methods=["GET"])
@login_required
@roles_required("doctor")
def get_doctor_availability():
    doctor = get_current_doctor()

    cache_key = build_cache_key("doctor_availability", doctor.id)
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify({"availability":cached, "source":"cache"}), 200
    
    today = date.today()
    end_date = today + timedelta(days=7)

    records = DoctorAvailability.query.filter(DoctorAvailability.doctor_id == doctor.id,DoctorAvailability.available_date >= today, DoctorAvailability.available_date <= end_date).all()

    data = [
        {
            "date": r.available_date.isoformat(),
            "start_time": r.start_time.strftime("%H:%M"),
            "end_time": r.end_time.strftime("%H:%M"),
        }
        for r in records 
    ]
    cache_set(cache_key, data, ttl=SHORT_TTL)
    return jsonify({"availability":data, "source":"database"}),200

@doctor_bp.route("/availability", methods=["POST"])
@login_required
@roles_required("doctor")
def set_availability():

    doctor = get_current_doctor()
    data = request.get_json()

    if not data or "date" not in data or "slots" not in data:
        return jsonify({"error":"Missing date or slots"}), 400
    
    try:
        avail_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error":"Invalid date"}), 400
    
    DoctorAvailability.query.filter_by(doctor_id = doctor.id, available_date = avail_date).delete()

    for time_str in data["slots"]:
        try:
            start_time = datetime.strptime(time_str, "%H:%M").time()

            dummy_date = datetime(2000, 1, 1, start_time.hour, start_time.minute)
            end_time = (dummy_date + timedelta(minutes=30)).time()

            slot = DoctorAvailability(doctor_id = doctor.id, available_date=avail_date, start_time=start_time, end_time=end_time)

            db.session.add(slot)
        except Exception:
            pass 
    db.session.commit()
    cache_delete(build_cache_key("doctor_availability", doctor.id))
    return jsonify({"message": "Availability updated"}), 200


#TREATMENT AND STATUS ROUTE
@doctor_bp.route("/appointments/<int:appointment_id>/treatment", methods=["POST"])
@login_required
@roles_required("doctor")
def add_treatment(appointment_id):
    doctor = get_current_doctor()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.id:
        return jsonify({"error":"Unauthorized Access"}), 403
    
    if appointment.status != APPOINTMENT_STATUS_COMPLETED:
        return jsonify({"error": "Appointment needs to be marked completed"}), 400
    data = request.get_json()
    diagnosis = data.get("diagnosis")
    prescription = data.get("prescription")
    notes = data.get("notes", "")
    visit_type = data.get("visit_type", "In-person")
    tests_done = data.get("tests_done", "")

    if not diagnosis or not prescription:
        return jsonify({"error": "Diagnosis and prescription are required"}), 400
    
    treatment = Treatment.query.filter_by(appointment_id = appointment.id).first()
    if treatment:
        treatment.diagnosis = diagnosis
        treatment.prescription = prescription
        treatment.notes = notes
        treatment.visit_type = visit_type
        treatment.tests_done = tests_done
    else:
        treatment = Treatment(
            appointment_id = appointment.id,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes,
            visit_type=visit_type,
            tests_done=tests_done
        )
        db.session.add(treatment)
    db.session.commit()
    return jsonify({"message":"Treatment saved successfully"}), 201


@doctor_bp.route("/appointments/history", methods=["GET"])
@login_required
@roles_required("doctor")
def get_doctor_appointment_history():
    doctor = get_current_doctor()
    appointments = Appointment.query.filter(Appointment.doctor_id == doctor.id).order_by(Appointment.appointment_date.desc()).all()
    return jsonify({
        "count":len(appointments),
        "appointments": [serialize_appointment_history(a) for a in appointments]
    }), 200

@doctor_bp.route("/appointments/<int:appointment_id>/complete", methods=["POST"])
@login_required
@roles_required("doctor")
def complete_appointment(appointment_id):
    doctor = get_current_doctor()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        validate_status_transition(appointment, APPOINTMENT_STATUS_COMPLETED, "doctor")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    appointment.status = APPOINTMENT_STATUS_COMPLETED
    db.session.commit()
    return jsonify({"message":"Appointment completed."}), 200

@doctor_bp.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
@login_required
@roles_required("doctor")
def cancel_appointment(appointment_id):
    doctor = get_current_doctor()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        validate_status_transition(appointment, APPOINTMENT_STATUS_CANCELLED, "doctor")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    appointment.status = APPOINTMENT_STATUS_CANCELLED
    db.session.commit()
    return jsonify({"message":"Appointment cancelled."}), 200

@doctor_bp.route("/patients/<int:patient_id>/history", methods=["GET"])
@login_required
@roles_required("doctor")
def view_patient_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    appointments = Appointment.query.filter_by(patient_id= patient_id).order_by(Appointment.appointment_date.desc()).all()

    return jsonify({
        "patient_name": patient.user.name,
        "history": [serialize_appointment_history(a) for a in appointments]
    }), 200