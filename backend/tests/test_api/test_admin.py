import pytest
import uuid
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.protocol import Protocol, ProtocolStep, SafetyCheck, TherapyType, EvidenceLevel, StepType
from app.core.security import hash_password, create_access_token


def get_unique_email(prefix="admin"):
    """Generate unique email for testing."""
    return f"{prefix}-{uuid.uuid4()}@example.com"


# Create test database tables
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session: Session):
    """Create a platform admin user for testing."""
    email = get_unique_email("admin")
    user = User(
        email=email,
        password_hash=hash_password("AdminPassword123!"),
        role=UserRole.PLATFORM_ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def patient_user(db_session: Session):
    """Create a patient user for testing unauthorized access."""
    email = get_unique_email("patient")
    user = User(
        email=email,
        password_hash=hash_password("PatientPassword123!"),
        role=UserRole.PATIENT,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user: User):
    """Create access token for admin user."""
    token_data = {"sub": admin_user.email, "role": admin_user.role.value}
    return create_access_token(token_data)


@pytest.fixture
def patient_token(patient_user: User):
    """Create access token for patient user."""
    token_data = {"sub": patient_user.email, "role": patient_user.role.value}
    return create_access_token(token_data)


@pytest.fixture
def sample_protocol(db_session: Session, admin_user: User):
    """Create a sample protocol for testing."""
    protocol = Protocol(
        name="Test Protocol",
        version="1.0",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="depression",
        evidence_level=EvidenceLevel.PHASE_3,
        overview="Test protocol overview",
        duration_weeks=12,
        total_sessions=8,
        evidence_sources=["https://example.com/study1"],
        created_by=admin_user.id,
        status="draft"
    )
    db_session.add(protocol)
    db_session.commit()
    db_session.refresh(protocol)
    return protocol


# ============================================================================
# Test Protocol Creation
# ============================================================================

def test_create_protocol_as_admin(client: TestClient, admin_token: str, db_session: Session):
    """Test creating a protocol with admin role."""
    response = client.post(
        "/api/v1/admin/protocols",
        json={
            "name": "Psilocybin for Depression",
            "version": "1.0",
            "therapy_type": "psilocybin",
            "condition_treated": "treatment_resistant_depression",
            "evidence_level": "phase_3_trial",
            "overview": "Evidence-based protocol for TRD",
            "duration_weeks": 12,
            "total_sessions": 6,
            "evidence_sources": ["https://example.com/study"]
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Psilocybin for Depression"
    assert data["status"] == "draft"
    assert data["therapy_type"] == "psilocybin"
    assert "id" in data


def test_create_protocol_without_auth(client: TestClient):
    """Test creating a protocol without authentication fails."""
    response = client.post(
        "/api/v1/admin/protocols",
        json={
            "name": "Test Protocol",
            "version": "1.0",
            "therapy_type": "psilocybin",
            "condition_treated": "depression",
            "evidence_level": "phase_3_trial"
        }
    )

    assert response.status_code == 403


def test_create_protocol_as_patient(client: TestClient, patient_token: str):
    """Test creating a protocol with patient role fails."""
    response = client.post(
        "/api/v1/admin/protocols",
        json={
            "name": "Test Protocol",
            "version": "1.0",
            "therapy_type": "psilocybin",
            "condition_treated": "depression",
            "evidence_level": "phase_3_trial"
        },
        headers={"Authorization": f"Bearer {patient_token}"}
    )

    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


# ============================================================================
# Test Protocol Update
# ============================================================================

def test_update_protocol_as_admin(client: TestClient, admin_token: str, sample_protocol: Protocol):
    """Test updating a protocol with admin role."""
    response = client.put(
        f"/api/v1/admin/protocols/{sample_protocol.id}",
        json={
            "name": "Updated Protocol Name",
            "overview": "Updated overview"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Protocol Name"
    assert data["overview"] == "Updated overview"
    assert data["version"] == "1.0"  # Unchanged


def test_update_nonexistent_protocol(client: TestClient, admin_token: str):
    """Test updating a non-existent protocol fails."""
    response = client.put(
        "/api/v1/admin/protocols/99999",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404


# ============================================================================
# Test Protocol Steps
# ============================================================================

def test_add_step_to_protocol(client: TestClient, admin_token: str, sample_protocol: Protocol):
    """Test adding a step to a protocol."""
    response = client.post(
        f"/api/v1/admin/protocols/{sample_protocol.id}/steps",
        json={
            "sequence_order": 1,
            "step_type": "screening",
            "title": "Initial Psychiatric Evaluation",
            "description": "Comprehensive psychiatric assessment",
            "duration_minutes": 90,
            "required_roles": ["therapist", "medical_director"],
            "clinical_scales": ["PHQ-9", "GAD-7"]
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Initial Psychiatric Evaluation"
    assert data["step_type"] == "screening"
    assert data["sequence_order"] == 1
    assert data["protocol_id"] == sample_protocol.id


def test_update_protocol_step(client: TestClient, admin_token: str, sample_protocol: Protocol, db_session: Session):
    """Test updating a protocol step."""
    # Create a step first
    step = ProtocolStep(
        protocol_id=sample_protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Original Title"
    )
    db_session.add(step)
    db_session.commit()
    db_session.refresh(step)

    response = client.put(
        f"/api/v1/admin/protocols/{sample_protocol.id}/steps/{step.id}",
        json={
            "title": "Updated Step Title",
            "duration_minutes": 120
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Step Title"
    assert data["duration_minutes"] == 120
    assert data["sequence_order"] == 1  # Unchanged


def test_delete_protocol_step(client: TestClient, admin_token: str, sample_protocol: Protocol, db_session: Session):
    """Test deleting a protocol step."""
    # Create a step first
    step = ProtocolStep(
        protocol_id=sample_protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Step to Delete"
    )
    db_session.add(step)
    db_session.commit()
    db_session.refresh(step)

    response = client.delete(
        f"/api/v1/admin/protocols/{sample_protocol.id}/steps/{step.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Step deleted successfully"

    # Verify step is actually deleted
    deleted_step = db_session.query(ProtocolStep).filter(ProtocolStep.id == step.id).first()
    assert deleted_step is None


# ============================================================================
# Test Safety Checks
# ============================================================================

def test_add_safety_check_to_step(client: TestClient, admin_token: str, sample_protocol: Protocol, db_session: Session):
    """Test adding a safety check to a protocol step."""
    # Create a step first
    step = ProtocolStep(
        protocol_id=sample_protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Screening Step"
    )
    db_session.add(step)
    db_session.commit()
    db_session.refresh(step)

    response = client.post(
        f"/api/v1/admin/protocols/{sample_protocol.id}/steps/{step.id}/safety-checks",
        json={
            "check_type": "absolute_contraindication",
            "condition": {"field": "psychosis_history", "operator": "equals", "value": True},
            "severity": "blocking",
            "override_allowed": "false",
            "evidence_source": "Clinical guidelines 2024"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["check_type"] == "absolute_contraindication"
    assert data["severity"] == "blocking"
    assert data["protocol_step_id"] == step.id


# ============================================================================
# Test Protocol Publishing
# ============================================================================

def test_publish_protocol(client: TestClient, admin_token: str, sample_protocol: Protocol):
    """Test publishing a protocol."""
    response = client.post(
        f"/api/v1/admin/protocols/{sample_protocol.id}/publish",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["id"] == sample_protocol.id


def test_publish_nonexistent_protocol(client: TestClient, admin_token: str):
    """Test publishing a non-existent protocol fails."""
    response = client.post(
        "/api/v1/admin/protocols/99999/publish",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404


# ============================================================================
# Test Protocol Deletion
# ============================================================================

def test_delete_protocol(client: TestClient, admin_token: str, sample_protocol: Protocol, db_session: Session):
    """Test deleting (archiving) a protocol."""
    response = client.delete(
        f"/api/v1/admin/protocols/{sample_protocol.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Protocol archived successfully"

    # Verify protocol is archived, not deleted
    db_session.refresh(sample_protocol)
    assert sample_protocol.status == "archived"


# ============================================================================
# Test Full Workflow
# ============================================================================

def test_full_protocol_creation_workflow(client: TestClient, admin_token: str, db_session: Session):
    """Test complete workflow: create → add steps → add safety checks → publish."""

    # Step 1: Create protocol
    create_response = client.post(
        "/api/v1/admin/protocols",
        json={
            "name": "MDMA for PTSD",
            "version": "2.0",
            "therapy_type": "mdma",
            "condition_treated": "ptsd",
            "evidence_level": "phase_3_trial",
            "overview": "MAPS Phase 3 protocol",
            "duration_weeks": 18,
            "total_sessions": 12
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_response.status_code == 201
    protocol_id = create_response.json()["id"]

    # Step 2: Add screening step
    step1_response = client.post(
        f"/api/v1/admin/protocols/{protocol_id}/steps",
        json={
            "sequence_order": 1,
            "step_type": "screening",
            "title": "Initial Assessment",
            "duration_minutes": 90
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert step1_response.status_code == 201
    step1_id = step1_response.json()["id"]

    # Step 3: Add preparation step
    step2_response = client.post(
        f"/api/v1/admin/protocols/{protocol_id}/steps",
        json={
            "sequence_order": 2,
            "step_type": "preparation",
            "title": "Preparatory Session",
            "duration_minutes": 60
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert step2_response.status_code == 201

    # Step 4: Add safety check to screening step
    safety_response = client.post(
        f"/api/v1/admin/protocols/{protocol_id}/steps/{step1_id}/safety-checks",
        json={
            "check_type": "absolute_contraindication",
            "condition": {"field": "cardiovascular_disease", "operator": "equals", "value": True},
            "severity": "blocking",
            "override_allowed": "false"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert safety_response.status_code == 201

    # Step 5: Publish protocol
    publish_response = client.post(
        f"/api/v1/admin/protocols/{protocol_id}/publish",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "active"

    # Verify final state
    protocol = db_session.query(Protocol).filter(Protocol.id == protocol_id).first()
    assert protocol.status == "active"
    assert len(protocol.steps) == 2
    assert len(protocol.steps[0].safety_checks) == 1
