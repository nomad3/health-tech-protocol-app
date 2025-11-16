from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database import Base


class TreatmentStatus(str, Enum):
    """Treatment plan status enumeration."""
    SCREENING = "screening"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class SessionStatus(str, Enum):
    """Treatment session status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TreatmentPlan(Base):
    """Treatment plan model representing a patient's treatment journey."""

    __tablename__ = "treatment_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=True)  # Nullable for solo practitioners
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    protocol_version = Column(String(50), nullable=False)
    status = Column(SQLEnum(TreatmentStatus), nullable=False)
    start_date = Column(DateTime, nullable=False)
    estimated_completion = Column(DateTime, nullable=True)
    customizations = Column(JSON, nullable=True)  # Protocol modifications
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    therapist = relationship("User", foreign_keys=[therapist_id])
    clinic = relationship("Clinic")
    protocol = relationship("Protocol")
    sessions = relationship("TreatmentSession", back_populates="treatment_plan")

    def __repr__(self):
        return f"<TreatmentPlan(id={self.id}, patient_id={self.patient_id}, status={self.status})>"


class TreatmentSession(Base):
    """Treatment session model representing individual treatment sessions."""

    __tablename__ = "treatment_sessions"

    id = Column(Integer, primary_key=True, index=True)
    treatment_plan_id = Column(Integer, ForeignKey("treatment_plans.id"), nullable=False)
    protocol_step_id = Column(Integer, ForeignKey("protocol_steps.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    therapist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String(50), nullable=False)  # in_person, telehealth
    status = Column(SQLEnum(SessionStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    treatment_plan = relationship("TreatmentPlan", back_populates="sessions")
    protocol_step = relationship("ProtocolStep")
    therapist = relationship("User")
    documentation = relationship("SessionDocumentation", back_populates="treatment_session", uselist=False)

    def __repr__(self):
        return f"<TreatmentSession(id={self.id}, status={self.status}, scheduled_at={self.scheduled_at})>"


class SessionDocumentation(Base):
    """Session documentation model for clinical notes, vitals, and assessments."""

    __tablename__ = "session_documentation"

    id = Column(Integer, primary_key=True, index=True)
    treatment_session_id = Column(Integer, ForeignKey("treatment_sessions.id"), nullable=False)
    vitals = Column(JSON, nullable=True)  # Array of timestamped vitals: BP, HR, temp, SpO2
    clinical_scales = Column(JSON, nullable=True)  # PHQ-9, GAD-7, MEQ30, etc.
    therapist_notes = Column(Text, nullable=True)
    patient_subjective_notes = Column(Text, nullable=True)
    adverse_events = Column(JSON, nullable=True)  # Array of adverse events
    decision_point_evaluations = Column(JSON, nullable=True)  # Array of decision point evaluations
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    treatment_session = relationship("TreatmentSession", back_populates="documentation")

    def __repr__(self):
        return f"<SessionDocumentation(id={self.id}, treatment_session_id={self.treatment_session_id})>"
