from flask import Flask,render_template,request,redirect,url_for
from flask import current_app as app
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
        if this_user:
            if this_user.password==password:
                if this_user.type==0:
                    return render_template("admin_dashboard.html",this_user=this_user)
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
        this_user=User.query.filter_by(username=username).first() # lhs->attribute, rhs-> form data
        if this_user:
            if this_user.password==password:
                if this_user.type==2:
                    return render_template("patient_dashboard.html",this_user=this_user)
                else:
                    message= "Unauthorized Access"
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
        if this_user:
            if this_user.password==password:
                if this_user.type==1:
                    return render_template("doctor_dashboard.html",this_user=this_user)
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
        user_name=Doctor.query.filter_by(username=username).first()
        user_email=Doctor.query.filter_by(email=email).first()
        if user_name or user_email:
            return "Doctor already exists"
        else:
            doctor=Doctor(username=username,password=password,email=email,
                          specialization=specialization,experience=experience)
            user=User(username=username,password=password,type=1)
            db.session.add(doctor)
            db.session.add(user)
            db.session.commit()
            doc_avail1=DoctorAvailability(doctor_id=doctor.id,shift_name="morning",
                                             start_time=slot1_start,end_time=slot1_end)
            doc_avai2=DoctorAvailability(doctor_id=doctor.id,shift_name="evening",
                                             start_time=slot2_start,end_time=slot2_end)
            db.session.add(doc_avail1)
            db.session.add(doc_avai2)
            db.session.commit()
            return "Doctor Added Successfully"
    return render_template("add_doctor.html")

