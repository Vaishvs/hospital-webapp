
from xmlrpc.client import Boolean
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Date, Time
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# This creates a local SQLite file named 'hospital.db'
DATABASE_URL = "sqlite:///./hospitalDB.db"

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a session local class for each request
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Creates a new database session for each request and ensures that the session is closed after the request is completed.
# This is important for managing database connections and resources efficiently.


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Base class for your database models
class Base(DeclarativeBase):
    pass


# PatientDB class is the database model for the patients table in the database. It defines the structure of the table and its columns. Each instance of this class represents a row in the patients table.
class PatientDB(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    blood_group = Column(String)
    allergies = Column(String)
    phone = Column(String)
    address = Column(String)


class DoctorDB(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    specialization = Column(String)
    license_number = Column(String)
    phone = Column(String)
    email = Column(String)
    is_active = Column(Boolean, default=True)


class AppointmentDB(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id"),
        nullable=False
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.doctor_id"),
        nullable=False
    )

    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)

    reason = Column(String, nullable=True)

    status = Column(String, default="pending", nullable=False)


class MedicalRecordDB(Base):
    __tablename__ = "medical_records"

    record_id = Column(Integer, primary_key=True, index=True)

    appointment_id = Column(
        Integer,
        ForeignKey("appointments.appointment_id"),
        nullable=False,
        unique=True
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id"),
        nullable=False
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.doctor_id"),
        nullable=False
    )

    diagnosis = Column(String, nullable=False)

    symptoms = Column(String, nullable=True)

    notes = Column(String, nullable=True)


class MedicalRecordHistoryDB(Base):
    __tablename__ = "medical_record_updates"

    update_id = Column(Integer, primary_key=True)

    record_id = Column(
        Integer,
        ForeignKey("medical_records.record_id"),
        nullable=False
    )

    diagnosis = Column(String, nullable=True)
    symptoms = Column(String, nullable=True)
    notes = Column(String, nullable=True)


class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
