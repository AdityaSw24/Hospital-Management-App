# Here we will define the database
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
    
    # Relationships with Doctors
    availabilities = db.relationship('DoctorAvailability', backref='doctor')
    appointments=db.relationship('Appointment',backref='doctor')
    department=db.relationship('Department',backref='doctors')
    
class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    shift_name = db.Column(db.String(20), nullable=False)   # e.g. 'morning', 'evening'
    start_time = db.Column(db.String(), nullable=False)         # e.g. 08:00:00
    end_time = db.Column(db.String(),nullable=False)    

    
class Patient(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(), unique=True,nullable=False)
    password= db.Column(db.String(),unique=True,nullable=False)
    email= db.Column(db.String(),unique=True,nullable=False)
    is_active=db.Column(db.Boolean, default=True, nullable=False)

    appointments=db.relationship('Appointment',backref='patient')
class Appointment(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    patient_id= db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id= db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date= db.Column(db.Date, nullable=False)
    time= db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Department(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    name= db.Column(db.String(), unique=True,nullable=False)
    descrption= db.Column(db.String(),unique=True,nullable=False)
    doctors_registered= db.Column(db.Integer(),unique=True,nullable=False)

class Treatment(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    appointment_id= db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    diagnosis= db.Column(db.String(), nullable=False)
    prescription= db.Column(db.String(), nullable=False)
