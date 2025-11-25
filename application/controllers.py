from flask import Flask,render_template,request,redirect,url_for
from flask import current_app as app
from datetime import datetime, timedelta
from .models import *

# @app.route will be defined here.

@app.route("/",methods=["GET","POST"])
def home():
    return render_template("home.html")

@app.route("/admin_login",methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        this_user=User.query.filter_by(username=username).first() # lhs->attribute, rhs-> form data
        doctors=Doctor.query.filter_by(is_active=True).all()
        patients=Patient.query.filter_by(is_active=True).all()
        if this_user:
            if this_user.password==password:
                if this_user.type==0:
                    return render_template("admin_dashboard.html",this_user=this_user,doctors=doctors,patients=patients)
                else:
                    message= "Unauthorized Access"
            else:
                message= "Incorrect Password"
        else:
            message= "User Not Found"
        return render_template("admin_login.html",message=message)

    return render_template("admin_login.html")

@app.route("/patient_login",methods=["GET","POST"])
def patient_login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        this_user=Patient.query.filter_by(username=username).first() # lhs->attribute, rhs-> form data
        if this_user:
            if this_user.password==password:
                departments=Department.query.all()
                return render_template("patient_dashboard.html",this_user=this_user,departments=departments)
            else:
                message= "Incorrect Password"
        else:
            message= "User Not Found"
        return render_template("patient_login.html",message=message)
    return render_template("patient_login.html")


@app.route("/doctor_login",methods=["GET","POST"])
def doctor_login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        this_user=User.query.filter_by(username=username).first() # lhs->attribute, rhs-> form data
        doctor_id=Doctor.query.filter_by(username=username).first().id
        upcoming_appointments=Appointment.query.filter_by(doctor_id=doctor_id,status="BOOKED").all()
        upcoming_patients=[]
        for id,appointment in enumerate(upcoming_appointments):
                patient_id=appointment.patient_id
                patient=Patient.query.filter_by(id=patient_id).first()
                upcoming_patients.append((id+1,patient))
        assigned_appointments=Appointment.query.filter_by(doctor_id=doctor_id,status='COMPLETED').all()
        assigned_patients=[]
        for id,appointment in enumerate(assigned_appointments):
                patient_id=appointment.patient_id
                patient=Patient.query.filter_by(id=patient_id).first()
                assigned_patients.append((id+1,patient))
        if this_user:
            if this_user.password==password:
                if this_user.type==1:
                    return render_template("doctor_dashboard.html",this_user=this_user,
                                           upcoming_patients=upcoming_patients,
                                           assigned_patients=assigned_patients)
                else:
                    message= "Unauthorized Access"
            else:
                message= "Incorrect Password"
        else:
            message= "User Not Found"
        return render_template("doctor_login.html",message=message)

    return render_template("doctor_login.html")

@app.route("/patient_register",methods=["GET","POST"])
def patient_register():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        email=request.form.get("email")
        user_name=Patient.query.filter_by(username=username).first()
        user_email=Patient.query.filter_by(email=email).first()
        if user_name or user_email:
            return "user already exists"
        else:
            patient=Patient(username=username,password=password,email=email)
            user=User(username=username,password=password,type=2)
            db.session.add(patient)
            db.session.add(user)
            db.session.commit()
            return "Registered Successfully"
    return render_template("patient_register.html")

@app.route("/add_doctor",methods=["GET","POST"])
def add_doctor():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        email=request.form.get("email")
        specialization=request.form.get("spec")
        experience=request.form.get("exp")
        slot1=request.form.get("morning_slot")
        slot2=request.form.get("evening_slot")
        slot1_start,slot1_end=slot1.split("|")
        slot2_start,slot2_end=slot2.split("|")
        shift_1=slot1_start + "-" + slot1_end + "AM"
        shift_2=slot2_start + "-" + slot2_end + "PM"
        doctor=Doctor(username=username,password=password,email=email,
                        specialization=specialization,experience=experience)
        user=User(username=username,password=password,type=1)
        db.session.add(doctor)
        db.session.add(user)
        db.session.commit()
        doc_schedule=DoctorAvailability(doctor_id=doctor.id,shift_1=shift_1,shift_2=shift_2)
        dept=Department.query.filter_by(name=specialization).first()
        if dept:
            dept.doctors_registered=dept.doctors_registered+1
        db.session.add(doc_schedule)
        db.session.add(dept)
        db.session.commit()
        return "Doctor Added Successfully"
    return render_template("add_doctor.html")

@app.route("/add_dept",methods=["GET","POST"])
def add_dept():
    if request.method=="POST":
        dept_name=request.form.get("dept_name")
        dept_info=request.form.get("dept_info")
        add_dept=Department(name=dept_name,descrption=dept_info)
        db.session.add(add_dept)
        db.session.commit()
        return "Department Added Successfully"
    return render_template("add_dept.html")

@app.route("/view_all_dept",methods=["GET"])
def view_all_dept():
    departments=Department.query.all()
    return render_template("view_all_departments.html",depts=departments)

@app.route("/patient/<int:patient_id>/department/<int:department_id>",methods=["GET","POST"])
def view_dept_info(department_id,patient_id):
    department=Department.query.filter_by(id=department_id).first()
    patient=Patient.query.filter_by(id=patient_id).first()
    return render_template("dept_info.html",department=department,patient=patient)

@app.route("/book_appointment/<int:department_id>/<int:doctor_id>/<int:patient_id>",methods=["GET","POST"])
def book_doctor_slot(doctor_id,patient_id,department_id):
    doctor=Doctor.query.filter_by(id=doctor_id).first()
    department=Department.query.filter_by(id=department_id).first()
    patient=Patient.query.filter_by(id=patient_id).first()
    doctor_availability=DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()
    today = datetime.today()
    doctor_schedule = [(today + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(1,8)]
    f_dict={}
    for day in doctor_schedule:
        f_dict[day]=[]
        for slot in doctor_availability:
            f_dict[day].append((slot.shift_1,slot.shift_2))
    if request.method=="POST":
        selected_slot=request.form.get("selected_slot")
        date,time=selected_slot.split("|")
        appointment=Appointment(patient_id=patient_id,doctor_id=doctor_id,
                                date=date,time=time,status="BOOKED")
        db.session.add(appointment)
        db.session.commit()
        return render_template("dept_info.html",patient=patient,department=department,doctor=doctor,message="Appointment Booked Successfully")
    return render_template("doctor_appointment_booking.html",patient=patient,department=department,doctor=doctor,f_dict=f_dict)

@app.route("/department/<int:department_id>/doctor_info/<int:doctor_id>",methods=["GET","POST"])
def doctor_info(doctor_id,department_id):
    doctor=Doctor.query.filter_by(id=doctor_id).first()
    department=Department.query.filter_by(id=department_id).first()
    return render_template("doctor_info.html",doctor=doctor,department=department)