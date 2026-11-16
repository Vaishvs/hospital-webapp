from datetime import timedelta

from typing_extensions import Annotated

from fastapi.security import OAuth2PasswordRequestForm

from auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_active_user, get_password_hash, require_role
from schemas import AppointmentResponse, Doctor, DoctorCreate, DoctorResponse, Patient, PatientCreate, PatientResponse, Appointment, MedicalRecord, MedicalRecordResponse, PatientUpdate, Token, User, UserRole
from sqlalchemy.orm import Session
from database import AppointmentDB, Base, MedicalRecordDB, UserDB, engine, get_db, PatientDB, DoctorDB
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
async def create_patient(
    patient: PatientCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):

    # Step 1: Create user account
    db_user = UserDB(
        username=patient.username,
        email=patient.email,
        hashed_password=get_password_hash(patient.password),
        role="patient",
        is_active=True
    )

    db.add(db_user)

    # Step 2: Generate user_id
    db.flush()

    # Step 3: Create patient profile
    db_patient = PatientDB(
        user_id=db_user.user_id,
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        blood_group=patient.blood_group,
        allergies=patient.allergies,
        phone=patient.phone,
        address=patient.address
    )

    db.add(db_patient)

    # Step 4: Save both records
    db.commit()
    db.refresh(db_patient)

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
def get_patients(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):
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
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):
    db_patient = db.query(PatientDB).filter(
        PatientDB.patient_id == patient_id
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
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):

    db_patient = db.query(PatientDB).filter(
        PatientDB.patient_id == patient_id
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

@app.delete("/patients/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):

    db_patient = db.query(PatientDB).filter(
        PatientDB.patient_id == patient_id
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


# Defines what the API sends back to the patient in the swagger response.
# It is a Pydantic model that specifies the fields and their types.
# The model_config is set to allow conversion from SQLAlchemy models to Pydantic models.

# -------------------------------------
# Patient updating his own information
# -------------------------------------
@app.patch("/patients/me/", response_model=PatientResponse)
def update_my_patient_profile(
    patient: PatientUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.PATIENT))
    ]
):
    # Find the patient profile belonging to the logged-in user
    db_patient = db.query(PatientDB).filter(
        PatientDB.user_id == current_user.user_id
    ).first()

    if db_patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    # Get only the fields provided by the patient
    update_data = patient.model_dump(exclude_unset=True)

    # Update the corresponding database attributes
    for key, value in update_data.items():
        setattr(db_patient, key, value)

    db.commit()
    db.refresh(db_patient)

    return db_patient

# ----------------------------------------------------------------------------------------------------------------------------
#                                         Doctors CRUD Operations
# ----------------------------------------------------------------------------------------------------------------------------@


# -------------------------
# Creating Doctors
# -------------------------


@app.post("/doctors/", response_model=DoctorResponse)
async def create_doctor(
    doctor: DoctorCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):
    # Step 1: Create the login account in users table
    db_user = UserDB(
        username=doctor.username,
        email=doctor.email,
        hashed_password=get_password_hash(doctor.password),
        role="doctor",
        is_active=True
    )

    db.add(db_user)

    # Step 2: Generate user_id without committing
    db.flush()

    # Step 3: Create the doctor profile
    db_doctor = DoctorDB(
        user_id=db_user.user_id,
        name=doctor.name,
        specialization=doctor.specialization,
        license_number=doctor.license_number,
        phone=doctor.phone,
        email=doctor.email,
        is_active=True
    )

    db.add(db_doctor)

    # Step 4: Save both records
    db.commit()

    db.refresh(db_doctor)

    return db_doctor
# -------------------------
# Retrieving Doctors
# -------------------------


@app.get("/doctors/", response_model=list[DoctorResponse])
async def get_doctors(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):
    doctors = db.query(DoctorDB).all()
    return doctors
# ---------------------------------
# Retrieving Doctors by Doctor ID
# ---------------------------------


@app.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):
    db_doctor = db.query(DoctorDB).filter(
        DoctorDB.doctor_id == doctor_id
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
async def update_doctor(
    doctor_id: int,
    doctor: DoctorCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        UserDB, Depends(require_role(UserRole.ADMIN))
    ]
):
    db_doctor = db.query(DoctorDB).filter(
        DoctorDB.doctor_id == doctor_id
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
    db: Annotated[Session, Depends(get_db)]

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
    db: Annotated[Session, Depends(get_db)]
):
    appointments = db.query(AppointmentDB).all()

    return appointments


# ----------------------------------------------
# Retrieving Appointments by Appointment ID
# -------------------------------------------------

@app.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    db_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.appointment_id == appointment_id
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
    db: Annotated[Session, Depends(get_db)]
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
    db: Annotated[Session, Depends(get_db)]
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
    db: Annotated[Session, Depends(get_db)]
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
    db: Annotated[Session, Depends(get_db)]
):
    medical_records = db.query(MedicalRecordDB).all()

    return medical_records


# -------------------------------------------------
# Retrieving Medical Records by Medical Record ID
# -------------------------------------------------

@app.get("/medical-records/{record_id}", response_model=MedicalRecordResponse)
def get_medical_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)]
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


# -----------------------------------------------------------
# Retrieving all Medical Records of a Patient by Patient ID
# --------------------------------------------------------------

@app.get("/patients/{patient_id}/medical-history")
def get_patient_medical_history(
    patient_id: int,
    db: Session = Depends(get_db)
):
    records = (
        db.query(MedicalRecordDB)
        .join(AppointmentDB)
        .filter(AppointmentDB.patient_id == patient_id)
        .all()
    )

    return records


# ------------------------------------------------------------
# Token Endpoints for Authentication and Authorization
# ---------------------------------------------------------------


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
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
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    return current_user

# There are actually two separate processes:
# Process 1: Generating the token
# login_for_access_token() → create_access_token() → JWT returned to Swagger.
# Process 2: Receiving the token
# The token is in now swagger and when you click on "Authorize" in Swagger, it sends the token in the Authorization header of subsequent requests.
# The get_current_user() function is called to decode the JWT and retrieve the user information from the database. This is done through the dependency injection mechanism of FastAPI,
# where the token is passed to get_current_user() via Depends(oauth2_scheme). The decoded user information is then returned to the endpoint that requires authentication.
# Swagger → Authorization header → OAuth2PasswordBearer → get_current_user(token) → jwt.decode().
# The connection between these two processes is the JWT returned in the HTTP response and subsequently sent back in the HTTP Authorization header.


# HOW SWAGGER AUTHENTICATION WORKS:
#
# 1. OAuth2PasswordBearer(tokenUrl="token") defines the OAuth2
#    authentication scheme.
#
# 2. FastAPI includes this configuration in its OpenAPI documentation.
#    Swagger UI reads it and automatically displays the Authorize button.
#
# 3. When we click Authorize, Swagger sends the username and password
#    to the /token endpoint.
#
# 4. login_for_access_token() calls authenticate_user() to verify
#    the credentials and create_access_token() to generate a JWT.
#
# 5. The JWT is returned to Swagger, which stores it for subsequent
#    protected API requests.
#
# 6. When a protected endpoint like /users/me/ is called, Swagger
#    automatically sends the JWT in the Authorization header:
#    Authorization: Bearer <JWT>
#
# 7. OAuth2PasswordBearer extracts the JWT from the Authorization
#    header and passes it to get_current_user().
#
# 8. get_current_user() decodes and validates the JWT using jwt.decode(),
#    retrieves the user from the database, and returns the user.
#
# 9. get_current_active_user() checks whether the user is active.
#
# IMPORTANT:
# - Manually executing POST /token generates a JWT.
# - Clicking Swagger's Authorize button calls POST /token again
#   and generates another JWT.
# - Both tokens may or may not be identical, depending on their payload
#   and expiration timestamp.
# - We don't need to manually execute POST /token before clicking
#   Authorize. Swagger can generate and store the token itself.
