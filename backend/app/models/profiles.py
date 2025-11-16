from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Clinic(Base):
    """Clinic model representing treatment clinics or solo practices."""

    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # clinic, solo_practice
    address = Column(Text, nullable=True)
    license_numbers = Column(JSON, nullable=True)  # Array of license numbers
    certifications = Column(JSON, nullable=True)  # Array of certifications
    protocols_enabled = Column(JSON, nullable=True)  # Array of protocol names
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    therapists = relationship("TherapistProfile", back_populates="clinic")

    def __repr__(self):
        return f"<Clinic(id={self.id}, name={self.name}, type={self.type})>"


class TherapistProfile(Base):
    """Therapist profile model with licensure and certification info."""

    __tablename__ = "therapist_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=True)
    license_type = Column(String(50), nullable=False)  # MD, PhD, LCSW, etc.
    license_number = Column(String(100), nullable=False)
    license_state = Column(String(10), nullable=False)
    specialties = Column(JSON, nullable=True)  # Array of specialties
    certifications = Column(JSON, nullable=True)  # Array of certifications
    protocols_certified = Column(JSON, nullable=True)  # Array of protocol names
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    clinic = relationship("Clinic", back_populates="therapists")

    def __repr__(self):
        return f"<TherapistProfile(id={self.id}, user_id={self.user_id}, license_type={self.license_type})>"


class PatientProfile(Base):
    """Patient profile model with medical history and contraindications."""

    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    medical_history = Column(JSON, nullable=True)  # Structured medical history
    medications = Column(JSON, nullable=True)  # Array of current medications
    contraindications = Column(JSON, nullable=True)  # Array of detected contraindications
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<PatientProfile(id={self.id}, user_id={self.user_id})>"
