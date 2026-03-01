from datetime import datetime, timedelta
from app.models import DoctorAvailability, Appointment, Doctor
from app.extensions import db
from app.utils.constants import APPOINTMENT_STATUS_BOOKED, APPOINTMENT_STATUS_CANCELLED, APPOINTMENT_STATUS_COMPLETED

class BookingError(Exception): pass
class DoctorNotFoundError(BookingError): pass
class SlotAlreadyBookedError(BookingError): pass
class PatientOverlapError(BookingError): pass
class OutsideAvailabilityError(BookingError): pass
class PastAppointmentError(BookingError): pass
class InvalidAppointmentStateError(BookingError): pass
class UnauthorizedAppointmentAccessError(BookingError): pass

def book_appointment(patient_id, doctor_id, appointment_date, appointment_time):
    doctor = Doctor.query.get(doctor_id)
    if not doctor: raise DoctorNotFoundError("Doctor not found")

    appt_dt = datetime.combine(appointment_date, appointment_time)
    if appt_dt < datetime.now():
        raise PastAppointmentError("Cannot book appointments in the past")
    if not _is_doctor_available(doctor_id, appointment_date, appointment_time):
        raise OutsideAvailabilityError("Doctor is not available at this time.")
    
    _check_doctor_slot_conflict(doctor_id, appointment_date, appointment_time)
    _check_patient_overlap(patient_id, appointment_time,appointment_date)

    new_appt = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status = APPOINTMENT_STATUS_BOOKED
    )
    db.session.add(new_appt)
    db.session.commit()
    return new_appt

def reschedule_appointment(appointment_id, patient_id, new_date, new_time):
    appt = Appointment.query.get(appointment_id)
    if not appt: raise BookingError("Appointment not found")
    if appt.patient_id != patient_id: raise UnauthorizedAppointmentAccessError("Not authorized")
    if appt.status != APPOINTMENT_STATUS_BOOKED: raise InvalidAppointmentStateError("Can only reschedule BOOKED appointments")

    _check_doctor_slot_conflict(appt.doctor_id, new_date, new_time)
    _check_patient_overlap(patient_id, new_time, exclude_appt_id = appointment_id)

    if not _is_doctor_available(appt.doctor_id, new_date, new_time):
        raise OutsideAvailabilityError("Doctor unavailable at new time")
    
    appt.appointment_date = new_date
    appt.appointment_time = new_time

    db.session.commit()
    return appt

def validate_status_transition(appointment, new_status, actor_role):

    if appointment.status == new_status:
        return True
    
    if appointment.status == APPOINTMENT_STATUS_CANCELLED:
        raise ValueError("Cannot change a cancelled appointment")
    
    if appointment.status == APPOINTMENT_STATUS_COMPLETED:
        raise ValueError("Cannot change a completed appointment")
    
    if new_status == APPOINTMENT_STATUS_COMPLETED and actor_role != 'doctor':
        raise ValueError("Only doctors can complete appointments")
    return True

#Helper Functions

def _is_doctor_available(doctor_id, date_obj, time_obj):
    slot = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.available_date == date_obj,
        DoctorAvailability.start_time <= time_obj,
        DoctorAvailability.end_time > time_obj
    ).first()

    return True if slot else False

def _check_doctor_slot_conflict(doctor_id, appointment_date, appointment_time):
    conflict = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status=APPOINTMENT_STATUS_BOOKED
    ).first()

    if conflict:
        raise SlotAlreadyBookedError("Slot already booked")
    
def _check_patient_overlap(patient_id, appointment_date, appointment_time, exclude_appt_id=None):
    query = Appointment.query.filter_by(
        patient_id=patient_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status=APPOINTMENT_STATUS_BOOKED,
    )
    if exclude_appt_id:
        query = query.filter(Appointment.id != exclude_appt_id)
    if query.first():
        raise PatientOverlapError("You already have an appointment at this time")