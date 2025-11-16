import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.treatment import TreatmentPlan, TreatmentSession, SessionDocumentation, TreatmentStatus, SessionStatus
from app.models.protocol import Protocol, ProtocolStep, TherapyType, EvidenceLevel, StepType
from app.models.user import User, UserRole
from app.database import SessionLocal


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_users(db_session: Session):
    """Create test users for treatment tests."""
    # Create patient
    patient = db_session.query(User).filter_by(email="patient@example.com").first()
    if not patient:
        patient = User(
            email="patient@example.com",
            password_hash="hashed_password",
            role=UserRole.PATIENT,
        )
        db_session.add(patient)

    # Create therapist
    therapist = db_session.query(User).filter_by(email="therapist@example.com").first()
    if not therapist:
        therapist = User(
            email="therapist@example.com",
            password_hash="hashed_password",
            role=UserRole.THERAPIST,
        )
        db_session.add(therapist)

    # Create admin for protocol creation
    admin = db_session.query(User).filter_by(email="admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            password_hash="hashed_password",
            role=UserRole.PLATFORM_ADMIN,
        )
        db_session.add(admin)

    db_session.commit()
    db_session.refresh(patient)
    db_session.refresh(therapist)
    db_session.refresh(admin)

    return {"patient": patient, "therapist": therapist, "admin": admin}


@pytest.fixture(scope="function")
def test_protocol(db_session: Session, test_users: dict):
    """Create a test protocol with steps."""
    protocol = Protocol(
        name="Test Psilocybin Protocol",
        version="1.0",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="depression",
        evidence_level=EvidenceLevel.PHASE_3,
        created_by=test_users["admin"].id,
    )
    db_session.add(protocol)
    db_session.commit()

    # Add a protocol step
    step = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Initial Screening",
        duration_minutes=60,
    )
    db_session.add(step)
    db_session.commit()
    db_session.refresh(protocol)
    db_session.refresh(step)

    return {"protocol": protocol, "step": step}


def test_create_treatment_plan(db_session: Session, test_users: dict, test_protocol: dict):
    """Test creating a treatment plan."""
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.SCREENING,
        start_date=datetime.utcnow(),
        estimated_completion=datetime.utcnow() + timedelta(weeks=12),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    assert treatment_plan.id is not None
    assert treatment_plan.patient_id == test_users["patient"].id
    assert treatment_plan.therapist_id == test_users["therapist"].id
    assert treatment_plan.protocol_id == test_protocol["protocol"].id
    assert treatment_plan.status == TreatmentStatus.SCREENING
    assert treatment_plan.created_at is not None


def test_treatment_plan_with_clinic(db_session: Session, test_users: dict, test_protocol: dict):
    """Test creating a treatment plan with a clinic_id."""
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        clinic_id=1,  # Nullable integer for now
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    assert treatment_plan.id is not None
    assert treatment_plan.clinic_id == 1


def test_treatment_plan_with_customizations(db_session: Session, test_users: dict, test_protocol: dict):
    """Test treatment plan with protocol customizations."""
    customizations = {
        "modified_steps": [1, 3],
        "additional_sessions": 2,
        "notes": "Patient requested extra integration sessions"
    }

    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
        customizations=customizations,
    )
    db_session.add(treatment_plan)
    db_session.commit()

    assert treatment_plan.customizations == customizations
    assert treatment_plan.customizations["additional_sessions"] == 2


def test_create_treatment_session(db_session: Session, test_users: dict, test_protocol: dict):
    """Test creating a treatment session."""
    # Create treatment plan first
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    # Create session
    session_time = datetime.utcnow() + timedelta(days=7)
    treatment_session = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=test_protocol["step"].id,
        scheduled_at=session_time,
        therapist_id=test_users["therapist"].id,
        location="in_person",
        status=SessionStatus.SCHEDULED,
    )
    db_session.add(treatment_session)
    db_session.commit()

    assert treatment_session.id is not None
    assert treatment_session.treatment_plan_id == treatment_plan.id
    assert treatment_session.protocol_step_id == test_protocol["step"].id
    assert treatment_session.status == SessionStatus.SCHEDULED
    assert treatment_session.location == "in_person"


def test_treatment_session_lifecycle(db_session: Session, test_users: dict, test_protocol: dict):
    """Test treatment session status transitions."""
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    # Create session
    treatment_session = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=test_protocol["step"].id,
        scheduled_at=datetime.utcnow(),
        therapist_id=test_users["therapist"].id,
        location="telehealth",
        status=SessionStatus.SCHEDULED,
    )
    db_session.add(treatment_session)
    db_session.commit()

    # Start session
    treatment_session.status = SessionStatus.IN_PROGRESS
    treatment_session.actual_start = datetime.utcnow()
    db_session.commit()

    assert treatment_session.status == SessionStatus.IN_PROGRESS
    assert treatment_session.actual_start is not None

    # Complete session
    treatment_session.status = SessionStatus.COMPLETED
    treatment_session.actual_end = datetime.utcnow()
    db_session.commit()

    assert treatment_session.status == SessionStatus.COMPLETED
    assert treatment_session.actual_end is not None


def test_treatment_plan_sessions_relationship(db_session: Session, test_users: dict, test_protocol: dict):
    """Test relationship between treatment plan and sessions."""
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    # Create multiple sessions
    session1 = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=test_protocol["step"].id,
        scheduled_at=datetime.utcnow() + timedelta(days=1),
        therapist_id=test_users["therapist"].id,
        location="in_person",
        status=SessionStatus.SCHEDULED,
    )
    session2 = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=test_protocol["step"].id,
        scheduled_at=datetime.utcnow() + timedelta(days=7),
        therapist_id=test_users["therapist"].id,
        location="telehealth",
        status=SessionStatus.SCHEDULED,
    )
    db_session.add_all([session1, session2])
    db_session.commit()

    db_session.refresh(treatment_plan)
    assert len(treatment_plan.sessions) == 2


def test_create_session_documentation(db_session: Session, test_users: dict, test_protocol: dict):
    """Test creating session documentation."""
    # Create treatment plan and session
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    treatment_session = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=test_protocol["step"].id,
        scheduled_at=datetime.utcnow(),
        therapist_id=test_users["therapist"].id,
        location="in_person",
        status=SessionStatus.COMPLETED,
        actual_start=datetime.utcnow(),
        actual_end=datetime.utcnow() + timedelta(hours=1),
    )
    db_session.add(treatment_session)
    db_session.commit()

    # Create documentation
    vitals = [
        {"timestamp": "2024-01-01T10:00:00Z", "BP": "120/80", "HR": 72, "temp": 98.6, "SpO2": 98},
        {"timestamp": "2024-01-01T11:00:00Z", "BP": "118/78", "HR": 68, "temp": 98.4, "SpO2": 99},
    ]

    clinical_scales = {
        "PHQ-9": {"score": 12, "interpretation": "moderate_depression"},
        "GAD-7": {"score": 8, "interpretation": "mild_anxiety"},
    }

    documentation = SessionDocumentation(
        treatment_session_id=treatment_session.id,
        vitals=vitals,
        clinical_scales=clinical_scales,
        therapist_notes="Patient showed good engagement during session.",
        patient_subjective_notes="Felt relaxed and introspective.",
    )
    db_session.add(documentation)
    db_session.commit()

    assert documentation.id is not None
    assert documentation.treatment_session_id == treatment_session.id
    assert len(documentation.vitals) == 2
    assert documentation.clinical_scales["PHQ-9"]["score"] == 12


def test_session_documentation_with_adverse_events(db_session: Session, test_users: dict, test_protocol: dict):
    """Test session documentation with adverse events."""
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    treatment_session = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=test_protocol["step"].id,
        scheduled_at=datetime.utcnow(),
        therapist_id=test_users["therapist"].id,
        location="in_person",
        status=SessionStatus.COMPLETED,
    )
    db_session.add(treatment_session)
    db_session.commit()

    adverse_events = [
        {
            "timestamp": "2024-01-01T10:30:00Z",
            "severity": "mild",
            "description": "Mild nausea reported",
            "intervention": "Provided water, symptoms resolved within 10 minutes"
        }
    ]

    documentation = SessionDocumentation(
        treatment_session_id=treatment_session.id,
        adverse_events=adverse_events,
        therapist_notes="Patient experienced mild nausea, resolved quickly.",
    )
    db_session.add(documentation)
    db_session.commit()

    assert len(documentation.adverse_events) == 1
    assert documentation.adverse_events[0]["severity"] == "mild"


def test_session_documentation_with_decision_points(db_session: Session, test_users: dict, test_protocol: dict):
    """Test session documentation with decision point evaluations."""
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    treatment_session = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=test_protocol["step"].id,
        scheduled_at=datetime.utcnow(),
        therapist_id=test_users["therapist"].id,
        location="in_person",
        status=SessionStatus.COMPLETED,
    )
    db_session.add(treatment_session)
    db_session.commit()

    decision_evaluations = [
        {
            "decision_point_id": 1,
            "criteria_met": True,
            "outcome": "proceed_to_dosing",
            "rationale": "Patient meets all safety criteria and shows good psychological readiness"
        }
    ]

    documentation = SessionDocumentation(
        treatment_session_id=treatment_session.id,
        decision_point_evaluations=decision_evaluations,
        therapist_notes="Patient cleared for dosing session.",
    )
    db_session.add(documentation)
    db_session.commit()

    assert len(documentation.decision_point_evaluations) == 1
    assert documentation.decision_point_evaluations[0]["outcome"] == "proceed_to_dosing"


def test_session_documentation_relationship(db_session: Session, test_users: dict, test_protocol: dict):
    """Test relationship between treatment session and documentation."""
    treatment_plan = TreatmentPlan(
        patient_id=test_users["patient"].id,
        therapist_id=test_users["therapist"].id,
        protocol_id=test_protocol["protocol"].id,
        protocol_version=test_protocol["protocol"].version,
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow(),
    )
    db_session.add(treatment_plan)
    db_session.commit()

    treatment_session = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=test_protocol["step"].id,
        scheduled_at=datetime.utcnow(),
        therapist_id=test_users["therapist"].id,
        location="in_person",
        status=SessionStatus.COMPLETED,
    )
    db_session.add(treatment_session)
    db_session.commit()

    documentation = SessionDocumentation(
        treatment_session_id=treatment_session.id,
        therapist_notes="Session completed successfully.",
    )
    db_session.add(documentation)
    db_session.commit()

    db_session.refresh(treatment_session)
    assert treatment_session.documentation is not None
    assert treatment_session.documentation.therapist_notes == "Session completed successfully."
