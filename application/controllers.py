from flask import Flask,render_template,request,redirect,url_for,session
from sqlalchemy import or_
from flask import current_app as app
from datetime import datetime, timedelta
from .models import *

# @app.route will be defined here.

def fetch_doctors_and_patients():
    doctors=Doctor.query.filter_by(is_active=True,is_deleted=False).all()
    patients=Patient.query.filter_by(is_active=True,is_deleted=False).all()
    return doctors,patients 

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
                    return redirect("/admin_dashboard")
                else:
                    message= "Unauthorized Access"
            else:
                message= "Incorrect Password"
        else:
            message= "User Not Found"
        return render_template("admin_login.html",message=message)

    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    this_user=User.query.filter_by(type=0).first()
    doctors,patients=fetch_doctors_and_patients()
    upcoming_appointments = (
        db.session.query(Appointment, Patient, Doctor)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.status == 'BOOKED')
        .all()
    )
    past_appointments = (
        db.session.query(Appointment, Patient, Doctor)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.status == 'COMPLETED')  
        .all()
    )
    return render_template("admin_dashboard.html",doctors=doctors,patients=patients,
                           this_user=this_user,upcoming_appointments=upcoming_appointments,
                           past_appointments=past_appointments)

@app.route("/patient_login",methods=["GET","POST"])
def patient_login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        this_user=User.query.filter_by(username=username).first()
        patient=Patient.query.filter_by(username=username,is_deleted=False,is_active=True).first() # lhs->attribute, rhs-> form data
        if patient:
            if patient.password==password:
                return redirect(f"/patient_dashboard/{patient.id}")
            else:
                message= "Incorrect Password"
        else:
            message= "User Not Found"
        return render_template("patient_login.html",message=message)
    return render_template("patient_login.html")

@app.route("/patient_dashboard/<int:patient_id>")
def patient_dashboard(patient_id):
    patient=Patient.query.filter_by(id=patient_id).first()
    departments=Department.query.all()
    appointments = (
        db.session.query(Appointment, Doctor, Patient)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .join(Patient, Appointment.patient_id == Patient.id)
        .filter(Appointment.patient_id == patient.id, Appointment.status == "BOOKED")
        .all()
    ) 
    return render_template("patient_dashboard.html",patient=patient,departments=departments,appointments=appointments)

def get_upcoming_patients(doctor_id):
    upcoming_appointments=Appointment.query.filter_by(doctor_id=doctor_id,status="BOOKED").all()
    upcoming_patients=[]
    for id,appointment in enumerate(upcoming_appointments):
            patient_id=appointment.patient_id
            patient=Patient.query.filter_by(id=patient_id).first()
            upcoming_patients.append((id+1,patient))
    return upcoming_patients

def get_assigned_patients(doctor_id):
    assigned_patients=[]
    assigned_appointments=Appointment.query.filter_by(doctor_id=doctor_id,status='COMPLETED').all()
    for id,appointment in enumerate(assigned_appointments):
                patient_id=appointment.patient_id
                patient=Patient.query.filter_by(id=patient_id).first()
                assigned_patients.append((id+1,patient))
    return assigned_patients

@app.route("/doctor_dashboard/<int:doctor_id>")
def doctor_dashboard(doctor_id):
    doctor=Doctor.query.filter_by(id=doctor_id,is_deleted=False,is_active=True).first()
    upcoming_patients=get_upcoming_patients(doctor_id)
    assigned_patients=get_assigned_patients(doctor_id)
    return render_template("doctor_dashboard.html",doctor=doctor,
                           upcoming_patients=upcoming_patients,
                           assigned_patients=assigned_patients)

@app.route("/doctor_login",methods=["GET","POST"])
def doctor_login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        this_user=User.query.filter_by(username=username).first()
        if this_user:
            doctor=Doctor.query.filter_by(username=username,is_deleted=False,is_active=True).first() # lhs->attribute, rhs-> form data
            doctor_id=doctor.id
            if doctor:
                if doctor.password==password:
                    return redirect(f"/doctor_dashboard/{doctor_id}")
                    
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
            return redirect("/patient_login")
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
        return redirect("/view_all_dept")
    return render_template("add_dept.html")

@app.route("/view_all_dept",methods=["GET"])
def view_all_dept():
    departments=Department.query.all()
    for dept in departments:
        dept.doctors_registered = db.session.query(Doctor).filter(
            Doctor.specialization == dept.name,
            Doctor.is_deleted == False
        ).count()
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
    f_dict=available_slots(doctor_id)
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

@app.route("/view_treatment_history/<int:patient_id>",methods=["GET","POST"])
def view_treatment_history(patient_id):
    patient=Patient.query.filter_by(id=patient_id).first()
    treatments = (
    db.session.query(Treatment, Doctor)
    .join(Doctor, Treatment.doctor_id == Doctor.id)
    .filter(Treatment.patient_id == patient_id)
    .all()
)   
    for treatment,doctor in treatments:
        print(treatment.visit_type)
    return render_template("view_patient_history.html",treatments=treatments,patient=patient)

@app.route("/update_patient_history/<int:patient_id>/<int:doctor_id>",methods=["GET","POST"])
def update_patient_history(patient_id,doctor_id):
    if request.method=="POST":
        appointment=Appointment.query.filter_by(patient_id=patient_id,doctor_id=doctor_id,status="BOOKED").first()
        doctor=Doctor.query.filter_by(id=doctor_id).first()
        department=Department.query.all()
        appointment_id=appointment.id
        visit_type=request.form.get("visit_type")
        test_done=request.form.get("test_done")
        diagnosis=request.form.get("diagnosis")
        prescription=request.form.get("prescription")
        medicines=request.form.get("medicines")
        # Collecting Data for passing to admin dashboard as before.
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
        #-------------------------------------------------------------------------------------------------
        treatment=Treatment(appointment_id=appointment_id,patient_id=patient_id,doctor_id=doctor_id,
                            visit_type=visit_type,test_done=test_done,diagnosis=diagnosis,
                            prescription=prescription,medicines=medicines)
        db.session.add(treatment)
        db.session.commit()
        return render_template("doctor_dashboard.html",doctor=doctor,
                                        upcoming_patients=upcoming_patients,
                                        assigned_patients=assigned_patients)
    return render_template("update_patient_history.html",patient_id=patient_id)

@app.route("/delete_doctor/<string:admin_username>/<int:doctor_id>")
def delete_doctor(doctor_id,admin_username):
    this_user=User.query.filter_by(username=admin_username).first()
    doctor=Doctor.query.filter_by(id=doctor_id,).first()
    user=User.query.filter_by(username=doctor.username).first()
    doctor.is_deleted=True
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/delete_patient/<int:patient_id>")
def delete_patient(patient_id):
    patient=Patient.query.filter_by(id=patient_id).first()
    user=User.query.filter_by(username=patient.username).first()
    patient.is_deleted=True
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/blacklist_patient/<int:patient_id>")
def blacklist_patient(patient_id):
    patient=Patient.query.filter_by(id=patient_id).first()
    patient.is_active=False
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/blacklist_doctor/<int:doctor_id>")
def blacklist_doctor(doctor_id):
    doctor=Doctor.query.filter_by(id=doctor_id).first()
    doctor.is_active=False
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/edit_patient/<int:patient_id>",methods=["GET","POST"])
def edit_patient(patient_id):
    patient=Patient.query.filter_by(id=patient_id).first()
    user=User.query.filter_by(username=patient.username).first()
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        email=request.form.get("email")
        # Updating the existing patient details
        patient.username=username
        patient.password=password
        patient.email=email
        user.username=username
        user.password=password
        db.session.commit()
        return redirect("/admin_dashboard")
    return render_template("edit_patient_profile.html",patient=patient)

@app.route("/edit_doctor_profile/<int:doctor_id>",methods=["GET","POST"])
def edit_doctor_profile(doctor_id):
    # Getting the doctor's present info
    availability=DoctorAvailability.query.filter_by(doctor_id=doctor_id).first()
    doctor=Doctor.query.filter_by(id=doctor_id).first()
    user=User.query.filter_by(username=doctor.username).first()
    if user:
        if request.method=="POST":
            # Getting the data from the forom
            username=request.form.get("username")
            password=request.form.get("password") 
            email=request.form.get("email")
            specialization=request.form.get("spec")
            experience=request.form.get("exp")
            slot1=request.form.get("morning_slot")
            slot2=request.form.get("evening_slot")
            # Updating the existing doctor details
            doctor.username=username
            doctor.password=password
            doctor.email=email
            doctor.specialization=specialization
            doctor.experience=experience
            slot1_start,slot1_end=slot1.split("|")
            slot2_start,slot2_end=slot2.split("|")
            availability.shift_1=slot1_start + "-" + slot1_end + "AM"
            availability.shift_2=slot2_start + "-" + slot2_end + "PM"
            user.username=username
            user.password=password
            db.session.commit()
            return redirect("/admin_dashboard")
    return render_template("edit_doctor_profile.html",doctor=doctor)

@app.route("/appointment_complete/<int:patient_id>/<int:doctor_id>")
def appointment_complete(patient_id,doctor_id):
    appointments = (
    db.session.query(Appointment, Doctor)
    .join(Doctor, Appointment.doctor_id == Doctor.id)
    .filter(
        Appointment.patient_id == patient_id,
        Appointment.doctor_id == doctor_id,
        Appointment.status == "BOOKED"
    )
    .order_by(Appointment.id.desc())
    .all()
)
    for appointment,doctor in appointments:
        appointment.status="COMPLETED"
        db.session.commit()
    return redirect(f"/doctor_dashboard/{doctor.id}")

@app.route("/appointment_canceled/<int:patient_id>/<int:doctor_id>")
def appointment_canceled(patient_id,doctor_id):
    appointments = (
    db.session.query(Appointment, Doctor)
    .join(Doctor, Appointment.doctor_id == Doctor.id)
    .filter(
        Appointment.patient_id == patient_id,
        Appointment.doctor_id == doctor_id,
        Appointment.status == "BOOKED"
    )
    .order_by(Appointment.id.desc())
    .all()
)
    for appointment,doctor in appointments:
        appointment.status="CANCELED"
        db.session.commit()
    return redirect(f"/doctor_dashboard/{doctor.id}")

@app.route("/patient_canceled_appoinment/<int:appointment_id>")
def patient_canceled_appoinment(appointment_id):
    appointment=Appointment.query.filter_by(id=appointment_id).order_by(Appointment.id.desc()).first()
    appointment.status="CANCELED"
    db.session.commit()
    return redirect(f"/patient_dashboard/{appointment.patient_id}")

@app.route("/search")
def search_1():
    search_word=request.args.get("search")
    key=request.args.get("key")
    if key=="patient":
        results= Patient.query.filter(
            or_(
                Patient.username==search_word,
                Patient.email==search_word
            
            )
            
        ).all()

    elif key == "doctor":
        results= Doctor.query.filter(
            or_(
                Doctor.username==search_word,
                Doctor.email==search_word
            
            ),
            Doctor.is_deleted==False
        ).all() 
    return render_template("results.html",results=results,key=key)

@app.route("/doctor&department_search")
def search_2():
    search_word=request.args.get("search")
    key=request.args.get("key")
    if key=="department":
        results= Department.query.filter(
            (
                Department.name==search_word
            )
        ).all()

    elif key == "doctor":
        results= Doctor.query.filter(
            or_(
                Doctor.username==search_word,
                Doctor.email==search_word,
                Doctor.specialization==search_word 
            
            ),
            Doctor.is_deleted==False
        ).all() 
    return render_template("results.html",results=results,key=key)

@app.route("/provide_availability/<int:doctor_id>",methods=["GET","POST"])
def provide_availability(doctor_id):
    doctor=Doctor.query.filter_by(id=doctor_id).first()
    f_dict=session.get('f_dict') or available_slots(doctor_id)
    if request.method=="POST":
        selected_slots=request.form.getlist("selected_slot")
        par_list=[x.split("|") for x in selected_slots]
        for slot in par_list:
            date=slot[0]
            time=slot[1]
            if f_dict[date][0][0]==time:
                f_dict[date][0][1]="BOOKED"
            elif f_dict[date][0][2]==time:
                f_dict[date][0][3]="BOOKED"
        session['f_dict']=f_dict
        return redirect(f"/doctor_dashboard/{doctor.id}")
    return render_template("provide_availability.html",doctor=doctor,f_dict=f_dict)

 
# Doctor available slots function
def available_slots(doctor_id):
    doctor_availability=DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()
    booked_slots=Appointment.query.filter_by(doctor_id=doctor_id,status="BOOKED").all()
    today = datetime.today()
    doctor_schedule = [(today + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(1,8)]
    f_dict={}
    for day in doctor_schedule:
        f_dict[day]=[]
        for slot in doctor_availability:
                f_dict[day].append([slot.shift_1,slot.status_shift_1,slot.shift_2,slot.status_shift_2])
    for slot in booked_slots:
        if slot.date in f_dict:
            for shifts in f_dict[slot.date]:
                if slot.time==shifts[0]:
                    shifts[1]="BOOKED"
                elif slot.time==shifts[2]:
                    shifts[3]="BOOKED"
    return f_dict


