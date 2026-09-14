from datetime import timedelta

from typing_extensions import Annotated

from fastapi.security import OAuth2PasswordRequestForm

from auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_active_user
from schemas import AppointmentResponse, Doctor, DoctorResponse, MedicalRecordHistoryResponse, Patient, PatientResponse, Appointment, MedicalRecord, MedicalRecordResponse, Token, User
from sqlalchemy.orm import Session
from database import AppointmentDB, Base, MedicalRecordDB, MedicalRecordHistoryDB, engine, get_db, PatientDB, DoctorDB
from enum import Enum
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field


# -------------------------
# Creates the FastAPI app
# -------------------------

app = FastAPI()


# ----------------------------------------------------------
# Creates the database tables based on the defined models
# -----------------------------------------------------------

Base.metadata.create_all(bind=engine)

# ------------------------------------------------------
# Temporary database (dictionary with 0 patients)
# ------------------------------------------------------


# patients = {}
# No need of this dictionary as we are using SQLAlchemy for database operations.
# You can remove this temporary database and implement the CRUD operations using the PatientDB model and the database session.

# ----------------------------------------------------------------------------------------------------------------------------
#                                         Patients CRUD Operations
# ----------------------------------------------------------------------------------------------------------------------------


# -------------------------
# Creating Patients
# -------------------------

@app.post("/patients/", response_model=PatientResponse)
def create_patient(
    patient: Patient,
    db: Session = Depends(get_db)
):

    db_patient = PatientDB(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        blood_group=patient.blood_group,
        allergies=patient.allergies,
        phone=patient.phone,
        address=patient.address
    )

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    # return {
    #     "patient_id": db_patient.id,
    #     "patient": db_patient
    # }
    return db_patient


# @app.post("/patients/")
# async def create_patient(patient: Patient):

#     patient_id = len(patients) + 1

#     patients[patient_id] = patient

#     return {
#         "patient_id": patient_id,
#         "patient": patient
#     }

# -------------------------
# Retrieveing   Patients
# -------------------------


# @app.get("/patients/")
# def getPatients():
#     return patients

@app.get("/patients/", response_model=list[PatientResponse])
def get_patients(db: Session = Depends(get_db)):

    patients = db.query(PatientDB).all()

    return patients

# -------------------------------------
# Searching  Patients by Patient ID
# -------------------------------------


# @app.get("/patients/{patient_id}")
# def get_patient(patient_id: int):

#     if patient_id not in patients:
#         raise HTTPException(
#             status_code=404,
#             detail="Patient not found"
#         )

#     return {
#         "patient_id": patient_id,
#         "patient": patients[patient_id]
#     }

@app.get("/patients/{patient_id}",
         response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    db_patient = db.query(PatientDB).filter(
        PatientDB.id == patient_id
    ).first()

    if db_patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return db_patient

# -------------------------------------
# Update Patient by Patient ID
# -------------------------------------


# @app.put("/patients/{patient_id}")
# def update_patient(
#     patient_id: int,
#     patient: Patient
# ):

#     if patient_id not in patients:
#         raise HTTPException(
#             status_code=404,
#             detail="Patient not found"
#         )

#     patients[patient_id] = patient

#     return {
#         "patient_id": patient_id,
#         "patient": patient
#     }

@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient: Patient,
    db: Session = Depends(get_db)
):

    db_patient = db.query(PatientDB).filter(
        PatientDB.id == patient_id
    ).first()

    if db_patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    db_patient.name = patient.name
    db_patient.age = patient.age
    db_patient.gender = patient.gender
    db_patient.blood_group = patient.blood_group
    db_patient.allergies = patient.allergies
    db_patient.phone = patient.phone
    db_patient.address = patient.address

    db.commit()
    db.refresh(db_patient)

    # return {
    #     "patient_id": db_patient.id,
    #     "patient": db_patient
    # }
    return db_patient

# -------------------------------------
# Delete Patient by Patient ID
# -------------------------------------


# @app.delete("/patients/{patient_id}")
# def delete_patient(patient_id: int):

#     if patient_id not in patients:
#         raise HTTPException(
#             status_code=404,
#             detail="Patient not found"
#         )

#     deleted_patient = patients.pop(patient_id)

#     return {
#         "message": "Patient deleted successfully",
#         "patient_id": patient_id,
#         "patient": deleted_patient
#     }

@app.delete("/patients/{patient_id}")  # No Patient response required here
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):

    db_patient = db.query(PatientDB).filter(
        PatientDB.id == patient_id
    ).first()

    if db_patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    db.delete(db_patient)
    db.commit()

    return {
        "message": "Patient deleted successfully",
        "patient_id": patient_id
    }


# ----------------------------------------------------------------------------------------------------------------------------
#                                         Doctors CRUD Operations
# ----------------------------------------------------------------------------------------------------------------------------


# -------------------------
# Creating Doctors
# -------------------------

@app.post("/doctors/", response_model=DoctorResponse)
def create_doctor(
    doctor: Doctor,
    db: Session = Depends(get_db)
):
    db_doctor = DoctorDB(
        name=doctor.name,
        specialization=doctor.specialization,
        license_number=doctor.license_number,
        phone=doctor.phone,
        email=doctor.email
    )

    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)

    return db_doctor

# -------------------------
# Retrieving Doctors
# -------------------------


@app.get("/doctors/", response_model=list[DoctorResponse])
def get_doctors(
    db: Session = Depends(get_db)
):
    doctors = db.query(DoctorDB).all()

    return doctors

# ---------------------------------
# Retrieving Doctors by Doctor ID
# ---------------------------------


@app.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    db_doctor = db.query(DoctorDB).filter(
        DoctorDB.id == doctor_id
    ).first()

    if db_doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return db_doctor

# ---------------------------------
# Updating Doctors by Doctor ID
# ---------------------------------


@app.put("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor: Doctor,
    db: Session = Depends(get_db)
):
    db_doctor = db.query(DoctorDB).filter(
        DoctorDB.id == doctor_id
    ).first()

    if db_doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    db_doctor.name = doctor.name
    db_doctor.specialization = doctor.specialization
    db_doctor.license_number = doctor.license_number
    db_doctor.phone = doctor.phone
    db_doctor.email = doctor.email

    db.commit()
    db.refresh(db_doctor)

    return db_doctor

# ----------------------------------------------------------------------------------------------------------------------------
#                                         Appointments CRUD Operations
# ----------------------------------------------------------------------------------------------------------------------------

# -------------------------
# Creating Appointments
# -------------------------


@app.post("/appointments/", response_model=AppointmentResponse)
def create_appointment(
    appointment: Appointment,
    db: Session = Depends(get_db)
):
    # 1. Check if patient exists
    db_patient = db.query(PatientDB).filter(
        PatientDB.patient_id == appointment.patient_id
    ).first()

    if not db_patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # 2. Check if doctor exists
    db_doctor = db.query(DoctorDB).filter(
        DoctorDB.doctor_id == appointment.doctor_id
    ).first()

    if not db_doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # 3. Check if doctor is active
    if not db_doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Doctor is not active"
        )

    # 4. Check if doctor is already booked
    existing_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.doctor_id == appointment.doctor_id,
        AppointmentDB.appointment_date == appointment.appointment_date,
        AppointmentDB.appointment_time == appointment.appointment_time,
        AppointmentDB.status == "confirmed"
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Doctor is already booked at this date and time"
        )

    # 5. Create new appointment
    db_appointment = AppointmentDB(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        reason=appointment.reason,
        status="pending"
    )

    # 6. Add to database
    db.add(db_appointment)

    # 7. Save changes
    db.commit()

    # 8. Get generated appointment_id
    db.refresh(db_appointment)

    return db_appointment


# -------------------------
# Retrieving Appointments
# -------------------------


@app.get("/appointments/", response_model=list[AppointmentResponse])
def get_appointments(
    db: Session = Depends(get_db)
):
    appointments = db.query(AppointmentDB).all()

    return appointments


# ----------------------------------------------
# Retrieving Appointments by Appointment ID
# -------------------------------------------------

@app.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    db_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.id == appointment_id
    ).first()

    if db_appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return db_appointment


# ----------------------------------------------
# Patching Appointments by Appointment ID
# -------------------------------------------------

@app.patch("/appointments/{appointment_id}/confirm")
def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    db_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.appointment_id == appointment_id
    ).first()

    if not db_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    if db_appointment.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending appointments can be confirmed"
        )

    # Check if doctor already has a other confirmed appointment
    existing_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.doctor_id == db_appointment.doctor_id,
        AppointmentDB.appointment_date == db_appointment.appointment_date,
        AppointmentDB.appointment_time == db_appointment.appointment_time,
        AppointmentDB.status == "confirmed",
        # if there is another appointment bookedat the same time
        AppointmentDB.appointment_id != appointment_id
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Doctor is already booked at this date and time"
        )

    db_appointment.status = "confirmed"

    db.commit()
    db.refresh(db_appointment)

    return db_appointment

# This patch operation handles both the cases. 1.Pending -> Cancelled 2. Confirmed -> Cancelled.
# It also checks if the appointment is already cancelled and raises an error in that case.


@app.patch("/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    db_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.appointment_id == appointment_id
    ).first()

    if not db_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    if db_appointment.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Appointment is already cancelled"
        )

    db_appointment.status = "cancelled"

    db.commit()
    db.refresh(db_appointment)

    return db_appointment


# ----------------------------------------------------------------------------------------------------------------------------
#                                         Medical Records CRUD Operations
# ----------------------------------------------------------------------------------------------------------------------------


# One appointment has one main medical record, and that medical record can have many updates/history entries.

@app.post("/medical-records/", response_model=MedicalRecordResponse)
def create_medical_record(
    record: MedicalRecord,
    db: Session = Depends(get_db)
):
    # 1. Check if appointment exists
    db_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.appointment_id == record.appointment_id
    ).first()

    if not db_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    # 2. Check if appointment is confirmed
    if db_appointment.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="Medical record can only be created for a confirmed appointment"
        )

    # 3. Check if medical record already exists
    existing_record = db.query(MedicalRecordDB).filter(
        MedicalRecordDB.appointment_id == record.appointment_id
    ).first()

    if existing_record:
        raise HTTPException(
            status_code=400,
            detail="Medical record already exists for this appointment"
        )

    # 4. Create medical record
    db_record = MedicalRecordDB(
        appointment_id=record.appointment_id,
        patient_id=record.patient_id,
        doctor_id=record.doctor_id,
        diagnosis=record.diagnosis,
        symptoms=record.symptoms,
        notes=record.notes
    )

    # 5. Add to database
    db.add(db_record)

    # 6. Save
    db.commit()

    # 7. Get generated record_id
    db.refresh(db_record)

    return db_record


# -----------------------------
# Retrieving Medical Records
# -----------------------------


@app.get("/medical-records/", response_model=list[MedicalRecordResponse])
def get_medical_records(
    db: Session = Depends(get_db)
):
    medical_records = db.query(MedicalRecordDB).all()

    return medical_records


# -------------------------------------------------
# Retrieving Medical Records by Medical Record ID
# -------------------------------------------------

@app.get("/medical-records/{record_id}", response_model=MedicalRecordResponse)
def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    medical_record = db.query(MedicalRecordDB).filter(
        MedicalRecordDB.record_id == record_id
    ).first()

    if medical_record is None:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    return medical_record
    db: Session = Depends(get_db)


# ----------------------------------------------------------------------------------------------------------------------------
#                                         Medical Records History CRUD Operations
# ----------------------------------------------------------------------------------------------------------------------------

# One appointment has one main medical record, and that medical record can have many updates/history entries.
# we want an append-only history/versioning design instead of overwriting the existing medical-record row therefore we will have a separate table for medical-record history entries. Each entry will have a foreign key to the main medical-record row and will contain the updated information along with a timestamp. This way, we can keep track of all changes made to a medical record over time without losing any previous data.

# URL                    OR                    Request body
# ↓                                             ↓
# /medical-records/10/updates                  "record_id": 10

# We need to decide whether we want to use the record_id from the URL or from the request body.
# Using the record_id from the URL is more RESTful and makes it clear which medical record we are updating.
# Therefore, we will use the record_id from the URL and not require it in the request body.
# So in the MedicalRecordUpdate schema,  we will not include the record_id field but it's still include in
# database model for MedicalRecordUpdateDB because we need to store it in the database as a foreign key to the main medical-record row.

# -------------------------------------------------
# Create Medical History by Medical Record ID
# -------------------------------------------------
@app.post("/medical-records/{record_id}/history", response_model=MedicalRecordHistoryResponse)
def create_medical_record_history(
    record_id: int,
    history: MedicalRecordHistory,
    db: Session = Depends(get_db)
):
    # Check if medical record exists
    db_record = db.query(MedicalRecordDB).filter(
        MedicalRecordDB.record_id == record_id
    ).first()

    if not db_record:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    # Create new history entry
    db_history = MedicalRecordHistoryDB(
        record_id=record_id,
        diagnosis=history.diagnosis,
        symptoms=history.symptoms,
        notes=history.notes
    )

    db.add(db_history)
    db.commit()
    db.refresh(db_history)

    return db_history
# -------------------------------------------------
# Retrieving Medical History by Medical Record ID
# -------------------------------------------------


@app.get("/medical-records/{record_id}/history", response_model=list[MedicalRecordHistoryResponse])
def get_medical_record_history(
    record_id: int,
    db: Session = Depends(get_db)
):
    # Check if medical record exists
    db_record = db.query(MedicalRecordDB).filter(
        MedicalRecordDB.record_id == record_id
    ).first()

    if not db_record:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    history = db.query(MedicalRecordHistoryDB).filter(
        MedicalRecordHistoryDB.record_id == record_id
    ).all()

    return history

# -------------------------------------------------
# Retrieving all Medical History by history id
# -------------------------------------------------


@app.get("/medical-record-history/{history_id}", response_model=MedicalRecordHistoryResponse)
def get_medical_record_history_entry(
    history_id: int,
    db: Session = Depends(get_db)
):
    db_history = db.query(MedicalRecordHistoryDB).filter(
        MedicalRecordHistoryDB.history_id == history_id
    ).first()

    if not db_history:
        raise HTTPException(
            status_code=404,
            detail="Medical record history not found"
        )

    return db_history


# ------------------------------------------------------------
# Token Endpoints for Authentication and Authorization
# ---------------------------------------------------------------


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user
