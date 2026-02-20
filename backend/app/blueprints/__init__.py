from app.blueprints.auth.routes import auth_bp
from app.blueprints.patient.routes import patient_bp
from app.blueprints.doctor.routes import doctor_bp
from app.blueprints.admin.routes import admin_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)