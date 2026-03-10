from uuid import uuid4
from flask_security.utils import hash_password
from datetime import date, time, datetime, timedelta 
from app import create_app
from app.extensions import db 
from app.models import User, Role, Department, Doctor, Patient, DoctorAvailability, Appointment, Treatment
from app.utils.constants import APPOINTMENT_STATUS_BOOKED, APPOINTMENT_STATUS_COMPLETED

def seed_admin():
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator account of HMS")
        db.session.add(admin_role)
        db.session.commit()

    admin_email = "admin@hms.com"
    admin_user = User.query.filter_by(email=admin_email).first()

    if not admin_user:
        admin_user =User(name = "Admin - HMS", email = admin_email, password = hash_password("admin@123"), fs_uniquifier=str(uuid4()), active = True)

        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created!")
    else:
        print("Admin User already exists.")

def seed_departments():
    departments = [
        ("Cardiology","Heart and Blood vessel related Treatments"),
        ("Neurology","Brain, Nerves and Spine related disorders"),
        ("Orthopedics","Bones, joints, and muscular system"),
        ("Oncology","Cancer Treatment and Diagnosis"),
        ("Dermatology","Skin, hair, and nail treatments"),
    ]

    for name, desc in departments:
        if not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name, description=desc))

    db.session.commit()
    print("Departments seeded!!")

def seed_doctors():
    doctor_role = Role.query.filter_by(name="doctor").first()
    if not doctor_role:
        doctor_role = Role(name="doctor", description="The Doctor is a medical professional who manages assigned patient appointments and provides treatment through the system. Doctors can view their schedules, update availability, complete or cancel appointments, and record diagnosis, prescriptions, and medical notes for each consultation.")
        db.session.add(doctor_role)
        db.session.commit()

    cardiology = Department.query.filter_by(name="Cardiology").first()
    neurology = Department.query.filter_by(name="Neurology").first()
    orthopedics = Department.query.filter_by(name="Orthopedics").first()
    oncology = Department.query.filter_by(name="Oncology").first()
    dermatology = Department.query.filter_by(name="Dermatology").first()

    doctors = [
        {
            "name":"Aryan Goyal",
            "email":"aryan@hms.com",
            "password":"doc@123",
            "department": cardiology,
            "qualification": "MD Cardiology",
            "experience": 8,
        },

        {
            "name":"Arnav Reddy",
            "email":"arnav@hms.com",
            "password":"doc@123",
            "department": neurology,
            "qualification": "MBBS",
            "experience": 9,
        },

        {
            "name":"Prashant Tiwari",
            "email":"prashant@hms.com",
            "password":"doc@123",
            "department": orthopedics,
            "qualification": "MS Orthopedics",
            "experience": 5,
        },

        {
            "name":"Nitish Bhatt",
            "email":"nitish@hms.com",
            "password":"doc@123",
            "department": oncology,
            "qualification": "MD Radiation Oncology",
            "experience": 2,
        },

        {
            "name":"Sairaj Nanda",
            "email":"sairaj@hms.com",
            "password":"doc@123",
            "department": dermatology,
            "qualification": "MD (Dermatology, Venereology & Leprosy)",
            "experience": 10,
        },
    ]

    for doc in doctors:
        if User.query.filter_by(email = doc["email"]).first():
            continue 

        user = User( name = doc["name"], email = doc["email"], password = hash_password(doc["password"]), fs_uniquifier=str(uuid4()), active=True)

        user.roles.append(doctor_role)
        db.session.add(user)
        db.session.commit()

        doctor = Doctor(
            user_id = user.id,
            department_id = doc["department"].id,
            qualification = doc["qualification"],
            experience = doc["experience"],
            is_active = True,
            description = "Specialist with over " + str(doc["experience"]) + "years of experience."
        )

        db.session.add(doctor)
        db.session.commit()

        print(f"Doctor seeded: {doc['name']} ({doc['email']})")


def seed_patients():
    patient_role = Role.query.filter_by(name="patient").first()
    if not patient_role:
        patient_role = Role(name="patient", description="The Patient is a user who can register on the system to book and manage medical appointments. Patients can search for doctors by specialization and availability, schedule or cancel appointments, and view their own appointment history along with diagnosis and treatment details provided by doctors.")
        db.session.add(patient_role)
        db.session.commit()

    patients = [
        {
            "name": "Ujjwal Sharma",
            "email": "ujjwal@gmail.com",
            "password": "pat@123",
            "phone": "9999999990",
            "address": "Kanpur",
        },

        {
            "name": "Shubham Thakur",
            "email": "shubham@gmail.com",
            "password": "pat@123",
            "phone": "9999999991",
            "address": "Pune",
        },

        {
            "name": "Prasann Gaurav",
            "email": "prasann@gmail.com",
            "password": "pat@123",
            "phone": "9999999992",
            "address": "Delhi",
        },

        {
            "name": "Abinesh K",
            "email": "abinesh@gmail.com",
            "password": "pat@123",
            "phone": "9999999993",
            "address": "Chennai",
        },

        {
            "name": "Shivang Saraswat",
            "email": "shivang@gmail.com",
            "password": "pat@123",
            "phone": "9999999994",
            "address": "Kanpur",
        },
    ]

    for pat in patients:
        if User.query.filter_by(email = pat["email"]).first():
            continue 

        user = User( name = pat["name"], email = pat["email"], password = hash_password(pat["password"]), fs_uniquifier=str(uuid4()), active=True)

        user.roles.append(patient_role)
        db.session.add(user)
        db.session.commit()

        patient = Patient(
            user_id = user.id,
            phone = pat["phone"],
            address = pat["address"],
            is_active = True,
        )

        db.session.add(patient)
        db.session.commit()

        print(f"Patient seeded: {pat['name']} ({pat['email']})")

def seed_doctor_availability():

    doctors = Doctor.query.all()

    target_dates = [date.today(), date.today() + timedelta(days=1)]

    count = 0
    for doctor in doctors:
        for target_date in target_dates:
            DoctorAvailability.query.filter_by(doctor_id = doctor.id, available_date = target_date).delete()

            start_hour = 10
            end_hour = 14

            for hour in range(start_hour, end_hour):

                slot1 = DoctorAvailability(doctor_id = doctor.id, available_date = target_date, start_time = time(hour, 0), end_time = time(hour, 30))
                db.session.add(slot1)

                slot2 = DoctorAvailability(doctor_id = doctor.id, available_date = target_date, start_time = time(hour, 30), end_time = time(hour + 1, 0))
                db.session.add(slot2)
                count += 2 
    db.session.commit()
    print(f" Doctor availability seeded ({count} slots generated)")

def seed_demo_appointments():

    doctors = Doctor.query.all()
    patients = Patient.query.all()

    appt_date = date.today() + timedelta(days=1)

    if not doctors or not patients:
        return
    
    for i, patient in enumerate(patients):
        doctor = doctors[i % len(doctors)]

        slot_time = time(10+i,0)

        exists = Appointment.query.filter_by( doctor_id=doctor.id, patient_id=patient.id, appointment_date = appt_date).first()

        if not exists:
            appt = Appointment(doctor_id = doctor.id, patient_id = patient.id, appointment_date = appt_date, appointment_time = slot_time, status = APPOINTMENT_STATUS_BOOKED)

            db.session.add(appt)
    db.session.commit()
    print(f"Demo appointments seeded for {appt_date}")

def seed_past_history():
    doctors = Doctor.query.all()
    patients = Patient.query.all()

    if not doctors or not patients:
        return
    
    past_date = date.today() - timedelta(days = 5)

    history_data = [
        {
            "diagnosis": "Viral Fever",
            "prescription": "Paracetamol 500mg (1-0-1) for 3 days.\nDrink plenty of fluids.",
            "notes": "Patient reported high fever and body ache. COVID test negative."
        },
        {
            "diagnosis": "Mild Migraine",
            "prescription": "Naproxen 250mg as needed.\nAvoid bright screens.",
            "notes": "Recurring headache on left side. BP Normal."
        },
        {
            "diagnosis": "Seasonal Allergy",
            "prescription": "Cetirizine 10mg at night.",
            "notes": "Runny nose and sneezing. Lungs clear."
        }
    ]
    print(f"Seeding past history for date: {past_date}...")

    for i in range(3):
        patient = patients[i]
        doctor = doctors[i % len(doctors)] 
        data = history_data[i]

        appt = Appointment(
            doctor_id=doctor.id,
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_time=time(10 + i, 0), 
            status=APPOINTMENT_STATUS_COMPLETED
        )
        db.session.add(appt)
        db.session.commit()

        treatment = Treatment(
            appointment_id=appt.id,
            diagnosis=data["diagnosis"],
            prescription=data["prescription"],
            notes=data["notes"]
        )
        db.session.add(treatment)
    
    db.session.commit()
    print("Past history (Appointments + Treatments) seeded!")

def run_seed():
    seed_admin()
    seed_departments()
    seed_doctors()
    seed_patients()
    seed_doctor_availability()
    seed_demo_appointments()
    seed_past_history()

    print("\n Database seeding complete!")

if __name__=="__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        run_seed()



