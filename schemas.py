from sqlite3 import Date, Time
from sqlalchemy.orm import Session
from database import PatientDB, engine, Base, get_db
from enum import Enum
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field


# -------------------------
# Patient Schema
# -------------------------

class BloodGroup(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class Patient(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(gt=0, lt=120)
    gender: Gender
    blood_group: BloodGroup | None = None
    allergies: str | None = None
    phone: str = Field(pattern=r"^[0-9]{10}$")
    address: str | None = None


# --------------------------------------------------------------------------------------
# Response model for Patient, used to return patient data from the database.
# It includes the patient's ID and other details. The model_config is set to allow
# conversion from SQLAlchemy models to Pydantic models.
# --------------------------------------------------------------------------------------


class PatientResponse(BaseModel):
    patient_id: int
    name: str
    age: int
    gender: str
    blood_group: BloodGroup | None = None
    allergies: str | None = None
    phone: str
    address: str | None = None

    model_config = {
        "from_attributes": True
    }


# -------------------------
# Doctor Schema
# -------------------------

class Doctor(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    specialization: str = Field(min_length=2, max_length=100)
    license_number: str = Field(min_length=2, max_length=50)
    phone: str = Field(pattern=r"^[0-9]{10}$")
    email: str = Field(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class DoctorResponse(BaseModel):
    doctor_id: int
    name: str
    specialization: str
    license_number: str
    phone: str
    email: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }


# -------------------------
# Appointment Schema
# -------------------------

class Appointment(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: Date
    appointment_time: Time
    reason: str | None = None


class AppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    appointment_date: Date
    appointment_time: Time
    reason: str | None = None

    model_config = {
        "from_attributes": True
    }


# -------------------------
# Medical Record Schema
# -------------------------

class MedicalRecord(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    symptoms: str | None = None
    notes: str | None = None


class MedicalRecordResponse(BaseModel):
    record_id: int
    appointment_id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    symptoms: str
    notes: str

    model_config = {
        "from_attributes": True
    }


class MMedicalRecordHistory(BaseModel):
    # record_id: int not required , will come from the URL
    diagnosis: str | None = None
    symptoms: str | None = None
    notes: str | None = None


class MedicalRecordHistoryResponse(BaseModel):
    update_id: int
    diagnosis: str | None = None
    symptoms: str | None = None
    notes: str | None = None


class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

# while creating a user, the user will provide username, email, password, and role.
# The is_active field will be controlled by the admin and not provided by the user.


class UserCreate(BaseModel):
    username: str
    email: str = Field(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str
    role: UserRole
    # is_active: bool this will be controlled by the admin, not user input


class UserResponse(BaseModel):
    user_id: int
    username: str  # never return password in response
    email: str
    role: UserRole
    is_active: bool

    model_config = {
        "from_attributes": True
    }

# What user information do I want to work with after the user has already been authenticated?


class User(BaseModel):
    username: str
    email: str = Field(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    role: UserRole
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
