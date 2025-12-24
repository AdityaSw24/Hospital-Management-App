# Here we will define the database
from sqlalchemy import and_
from .database import db

# case 1 : import from .database => models.py will look in the current directory for database.py
# case 2 : import from database => models.py will look in the current directory for database.py

class User(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(),unique=True,nullable=False)
    password= db.Column(db.String(),nullable=False)
    type= db.Column(db.Integer(),nullable=False) # 0-admin,1-doctor,2-patient

class Admin(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(), unique=True,nullable=False)
    password= db.Column(db.String(),nullable=False)

class Doctor(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(), unique=True,nullable=False)
    password= db.Column(db.String(),nullable=False)
    email= db.Column(db.String(),unique=True,nullable=False)
    specialization = db.Column(db.String(),db.ForeignKey('department.name'),nullable=False)
    experience=db.Column(db.Integer(),nullable=False)
    is_active=db.Column(db.Boolean, default=True, nullable=False)
    is_deleted=db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships with Doctors
    availabilities = db.relationship('DoctorAvailability', backref='doctor')
    appointments=db.relationship('Appointment',backref='doctor')
    
class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id',ondelete="CASCADE"), nullable=False)
    shift_1 = db.Column(db.String(), nullable=False)
    status_shift_1 = db.Column(db.String(20), default="AVAILABLE", nullable=False)
    shift_2 = db.Column(db.String(), nullable=False)
    status_shift_2 = db.Column(db.String(20), default="AVAILABLE", nullable=False)
    
class Patient(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(), unique=True,nullable=False)
    password= db.Column(db.String(),nullable=False)
    email= db.Column(db.String(),unique=True,nullable=False)
    is_active=db.Column(db.Boolean, default=True, nullable=False)
    is_deleted=db.Column(db.Boolean, default=False, nullable=False)

    appointments=db.relationship('Appointment',backref='patient')
class Appointment(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    patient_id= db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id= db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date= db.Column(db.String(), nullable=False)
    time= db.Column(db.String(), nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Department(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    name= db.Column(db.String(), unique=True,nullable=False)
    descrption= db.Column(db.String(),nullable=False)
    doctors_registered= db.Column(db.Integer(),unique=False,default=0,nullable=False)

Department.doctors = db.relationship(
    'Doctor',
    primaryjoin=and_(
        Department.name == Doctor.specialization,
        Doctor.is_deleted == False
    ),
    backref='department'  # Creates doctor.department
)
class Treatment(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    appointment_id= db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    patient_id= db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id= db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    visit_type= db.Column(db.String(), nullable=False)
    test_done= db.Column(db.String(), nullable=False)
    diagnosis= db.Column(db.String(), nullable=False)
    prescription= db.Column(db.String(), nullable=False)
    medicines=db.Column(db.String())
