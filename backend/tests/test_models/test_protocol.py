import pytest
from sqlalchemy.orm import Session
from app.models.protocol import Protocol, ProtocolStep, StepType, TherapyType, EvidenceLevel
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
