from app.extensions import db 
from flask_security import UserMixin, RoleMixin
from datetime import datetime 

# Association Table
roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')), db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

#Role Model
class Role(db.Model, RoleMixin):
    __tablename__='role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(30), unique=True)
    description = db.Column(db.String(255))

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable = False)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users',lazy='dynamic'))

    doctor = db.relationship('Doctor', backref = 'user', uselist = False)
    patient = db.relationship('Patient', backref = 'user', uselist = False)

# department model
class Department(db.Model):
    __tablename__='department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique = True, nullable= False)
    description = db.Column(db.String(100))
    doctors = db.relationship('Doctor', backref='department', lazy=True)

#Doctor Model
class Doctor(db.Model):
    __tablename__='doctor'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)

    qualification = db.Column(db.String(50))
    description = db.Column(db.String(255))
    experience = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default = True)

    availabilities = db.relationship('DoctorAvailability', backref='doctor',cascade='all,delete-orphan')

# Patient User
class Patient(db.Model):
    __tablename__ ='patient'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable = False)
    date_of_birth = db.Column(db.Date)
    phone = db.Column(db.String(12))
    address = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

# Doctor Availability Model
class DoctorAvailability(db.Model):
    __tablename__='doctor_availability'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'),nullable=False)
    available_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time= db.Column(db.Time, nullable=False)
    __table_args__ = (db.UniqueConstraint('doctor_id','available_date','start_time', 'end_time', name = 'uq_doctor_availability_slot'),)

# Export Jobs Model
class ExportJob(db.Model):
    __tablename__ = 'export_job'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_type = db.Column(db.String(30))
    status = db.Column(db.String(20), default="PENDING")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(100))
    completed_at = db.Column(db.DateTime)

# Treatement Model
class Treatment(db.Model):
    __tablename__='treatment'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Notification Log Modek
class NotificationLog(db.Model):
    __tablename__='notification_log'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)
    notification_type = db.Column(db.String(20),nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), default='SENT')
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

# Appointment Model
class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

    appointment_date = db.Column(db.Date, nullable= False)
    appointment_time = db.Column(db.Time, nullable = False)
    status = db.Column(db.String(20), default="BOOKED")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref=db.backref('appointment', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('appointment', lazy=True))

    treatment = db.relationship('Treatment', backref='appointment', uselist=False)
