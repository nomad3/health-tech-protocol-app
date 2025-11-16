from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class TherapyType(str, Enum):
    """Therapy type enumeration for protocol-based medical treatments."""
    # Psychedelics
    PSILOCYBIN = "psilocybin"
    MDMA = "mdma"
    KETAMINE = "ketamine"
    LSD = "lsd"
    IBOGAINE = "ibogaine"

    # Hormone Therapy
    TESTOSTERONE = "testosterone"
    ESTROGEN = "estrogen"
    GROWTH_HORMONE = "growth_hormone"
    PEPTIDES = "peptides"

    # Cancer Treatments
    CHEMOTHERAPY = "chemotherapy"
    IMMUNOTHERAPY = "immunotherapy"
    RADIATION = "radiation"

    # Regenerative Medicine
    STEM_CELL = "stem_cell"
    PLATELET_RICH_PLASMA = "platelet_rich_plasma"
    EXOSOME = "exosome"

    # Emerging Treatments
    GENE_THERAPY = "gene_therapy"
    CRISPR = "crispr"
    CAR_T = "car_t"
    LONGEVITY = "longevity"

    # General
    OTHER = "other"


class EvidenceLevel(str, Enum):
    """Evidence level enumeration."""
    FDA_APPROVED = "fda_approved"
    PHASE_3 = "phase_3_trial"
    PHASE_2 = "phase_2_trial"
    PHASE_1 = "phase_1_trial"
    PRECLINICAL = "preclinical"
    CLINICAL_PRACTICE = "clinical_practice"


class StepType(str, Enum):
    """Protocol step type enumeration."""
    SCREENING = "screening"
    PREPARATION = "preparation"
    DOSING = "dosing"
    INTEGRATION = "integration"
    DECISION_POINT = "decision_point"
    FOLLOWUP = "followup"


class Protocol(Base):
    """Protocol model representing treatment protocols."""

    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft, active, archived
    therapy_type = Column(SQLEnum(TherapyType), nullable=False)
    condition_treated = Column(String(255), nullable=False)
    evidence_level = Column(SQLEnum(EvidenceLevel), nullable=False)
    overview = Column(Text)
    duration_weeks = Column(Integer)
    total_sessions = Column(Integer)
    evidence_sources = Column(JSON)  # Array of evidence sources
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    steps = relationship("ProtocolStep", back_populates="protocol", order_by="ProtocolStep.sequence_order")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Protocol(id={self.id}, name={self.name}, version={self.version})>"


class ProtocolStep(Base):
    """Protocol step model representing individual steps in a protocol."""

    __tablename__ = "protocol_steps"

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    step_type = Column(SQLEnum(StepType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer)
    required_roles = Column(JSON)  # Array of required roles
    documentation_template_id = Column(Integer, nullable=True)

    # Decision point specific fields
    evaluation_rules = Column(JSON)  # Decision logic
    branch_outcomes = Column(JSON)  # Possible outcomes

    # Clinical scales and monitoring
    clinical_scales = Column(JSON)  # Array of scale names
    vitals_monitoring = Column(JSON)  # Vitals monitoring config

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    protocol = relationship("Protocol", back_populates="steps")
    safety_checks = relationship("SafetyCheck", back_populates="protocol_step")

    def __repr__(self):
        return f"<ProtocolStep(id={self.id}, title={self.title}, type={self.step_type})>"


class SafetyCheck(Base):
    """Safety check model for contraindications and risk factors."""

    __tablename__ = "safety_checks"

    id = Column(Integer, primary_key=True, index=True)
    protocol_step_id = Column(Integer, ForeignKey("protocol_steps.id"), nullable=False)
    check_type = Column(String(100), nullable=False)  # absolute_contraindication, relative_contraindication, risk_factor
    condition = Column(JSON, nullable=False)  # Condition definition
    severity = Column(String(50), nullable=False)  # blocking, warning, info
    override_allowed = Column(String(10), default="false", nullable=False)
    override_requirements = Column(JSON)  # Requirements for override
    evidence_source = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    protocol_step = relationship("ProtocolStep", back_populates="safety_checks")

    def __repr__(self):
        return f"<SafetyCheck(id={self.id}, type={self.check_type}, severity={self.severity})>"
