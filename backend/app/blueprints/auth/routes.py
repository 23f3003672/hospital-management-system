from flask import Blueprint, request, jsonify
from flask_security import login_user, logout_user, current_user
from flask_security.utils import verify_password, hash_password
from uuid import uuid4
from app.extensions import db
from app.models import User, Role, Patient, Doctor

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid Request"}), 400
    email = data.get("email")
    password= data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and Password are required."}), 400
    
    user = User.query.filter_by(email=email).first()

    if not user or not verify_password(password, user.password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    if not user.active:
        return jsonify({"message": "Accoun is disabled.Kindly contact HMS administration."}), 403
    
    if user.has_role("doctor"):
        if user.doctor and not user.doctor.is_active:
            return jsonify({"message":"Account is blacklisted. Contact HMS Administration."}), 403
        
    if user.has_role("patient"):
        if user.patient and not user.patient.is_active:
            return jsonify({"message":"Account is blacklisted. Contact HMS Administration."}), 403
        
    login_user(user)
    token = user.get_auth_token()
    role = user.roles[0].name if user.roles else "patient"

    return jsonify({
        "message": "Login Successful",
        "token": token,
        "role": role,
        "email": user.email,
        "id": user.id
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    if not current_user.is_authenticated:
        return jsonify({"message":"Not logged in"}), 401
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route("/register", methods=["POST"])
def register_patient():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid Request"}), 400
    
    name = data.get("name")
    email = data.get("email")
    password= data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "Name, Email and Password are required."}), 400
    
    if len(password) < 6:
        return jsonify({"message": "Password must be atleast 6 characters"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists. Please Login"}), 400
    
    patient_role = Role.query.filter_by(name="patient").first()
    if not patient_role:
        return jsonify({"message": "Patient role not found."}), 500
    
    user = User(name=name, email=email, password=hash_password(password),fs_uniquifier=str(uuid4()), active=True)

    user.roles.append(patient_role)
    db.session.add(user)
    db.session.commit()

    patient = Patient(user_id=user.id)
    db.session.add(patient)
    db.session.commit()

    return jsonify({"message": "Patient registration successful!"}), 201