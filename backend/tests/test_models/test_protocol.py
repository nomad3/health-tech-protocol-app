import pytest
from sqlalchemy.orm import Session
from app.models.protocol import Protocol, ProtocolStep, SafetyCheck, StepType, TherapyType, EvidenceLevel
from app.models.user import User, UserRole
from app.database import SessionLocal


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_user(db_session: Session):
    """Create a test user for protocol creation."""
    # Try to find existing user first
    user = db_session.query(User).filter_by(email="testuser@example.com").first()
    if not user:
        user = User(
            email="testuser@example.com",
            password_hash="hashed_password",
            role=UserRole.PLATFORM_ADMIN,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


def test_create_protocol(db_session: Session, test_user: User):
    """Test creating a protocol."""
    protocol = Protocol(
        name="Psilocybin for Depression",
        version="1.0",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="treatment_resistant_depression",
        evidence_level=EvidenceLevel.PHASE_3,
        created_by=test_user.id,
    )
    db_session.add(protocol)
    db_session.commit()

    assert protocol.id is not None
    assert protocol.name == "Psilocybin for Depression"
    assert protocol.status == "draft"
    assert protocol.created_at is not None


def test_create_protocol_step(db_session: Session, test_user: User):
    """Test creating protocol steps."""
    protocol = Protocol(
        name="Test Protocol",
        version="1.0",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="depression",
        evidence_level=EvidenceLevel.PHASE_3,
        created_by=test_user.id,
    )
    db_session.add(protocol)
    db_session.commit()

    step = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Initial Psychiatric Evaluation",
        description="Comprehensive psychiatric assessment",
        duration_minutes=90,
    )
    db_session.add(step)
    db_session.commit()

    assert step.id is not None
    assert step.protocol_id == protocol.id
    assert step.step_type == StepType.SCREENING


def test_protocol_steps_relationship(db_session: Session, test_user: User):
    """Test protocol-steps relationship."""
    protocol = Protocol(
        name="Test Protocol",
        version="1.0",
        therapy_type=TherapyType.MDMA,
        condition_treated="ptsd",
        evidence_level=EvidenceLevel.FDA_APPROVED,
        created_by=test_user.id,
    )
    db_session.add(protocol)
    db_session.commit()

    step1 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Step 1",
    )
    step2 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=2,
        step_type=StepType.PREPARATION,
        title="Step 2",
    )
    db_session.add_all([step1, step2])
    db_session.commit()

    # Refresh protocol to load steps
    db_session.refresh(protocol)
    assert len(protocol.steps) == 2
    assert protocol.steps[0].sequence_order == 1
    assert protocol.steps[1].sequence_order == 2


def test_create_safety_check(db_session: Session, test_user: User):
    """Test creating a safety check."""
    protocol = Protocol(
        name="Test Protocol",
        version="1.0",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="depression",
        evidence_level=EvidenceLevel.PHASE_3,
        created_by=test_user.id,
    )
    db_session.add(protocol)
    db_session.commit()

    step = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Screening Step",
    )
    db_session.add(step)
    db_session.commit()

    safety_check = SafetyCheck(
        protocol_step_id=step.id,
        check_type="absolute_contraindication",
        condition={"diagnosis": "psychosis"},
        severity="blocking",
        override_allowed="false",
    )
    db_session.add(safety_check)
    db_session.commit()

    assert safety_check.id is not None
    assert safety_check.check_type == "absolute_contraindication"
    assert safety_check.severity == "blocking"
    assert safety_check.protocol_step_id == step.id


def test_safety_check_relationship(db_session: Session, test_user: User):
    """Test protocol step to safety checks relationship."""
    protocol = Protocol(
        name="Test Protocol",
        version="1.0",
        therapy_type=TherapyType.MDMA,
        condition_treated="ptsd",
        evidence_level=EvidenceLevel.FDA_APPROVED,
        created_by=test_user.id,
    )
    db_session.add(protocol)
    db_session.commit()

    step = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Screening Step",
    )
    db_session.add(step)
    db_session.commit()

    check1 = SafetyCheck(
        protocol_step_id=step.id,
        check_type="absolute_contraindication",
        condition={"condition": "cardiovascular_disease"},
        severity="blocking",
        override_allowed="false",
    )
    check2 = SafetyCheck(
        protocol_step_id=step.id,
        check_type="relative_contraindication",
        condition={"condition": "hypertension"},
        severity="warning",
        override_allowed="true",
    )
    db_session.add_all([check1, check2])
    db_session.commit()

    db_session.refresh(step)
    assert len(step.safety_checks) == 2
    assert step.safety_checks[0].severity == "blocking"
    assert step.safety_checks[1].severity == "warning"
