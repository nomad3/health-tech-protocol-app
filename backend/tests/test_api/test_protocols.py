import pytest
import uuid
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.protocol import Protocol, ProtocolStep, TherapyType, EvidenceLevel, StepType
from app.core.security import hash_password


def get_unique_email(prefix="user"):
    """Generate unique email for testing."""
    return f"{prefix}-{uuid.uuid4()}@example.com"


# Create test database tables
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    # Clean up protocols and users from previous test runs
    session.query(ProtocolStep).delete()
    session.query(Protocol).delete()
    session.query(User).delete()
    session.commit()
    yield session
    session.rollback()
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
    """Create an admin user for testing."""
    user = User(
        email=get_unique_email("admin"),
        password_hash=hash_password("Password123!"),
        role=UserRole.PLATFORM_ADMIN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_protocols(db_session: Session, admin_user: User):
    """Create sample protocols for testing."""
    protocols = []

    # Psilocybin Protocol
    psilocybin_protocol = Protocol(
        name="Psilocybin for Treatment-Resistant Depression",
        version="1.0",
        status="active",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="treatment_resistant_depression",
        evidence_level=EvidenceLevel.PHASE_3,
        overview="Evidence-based psilocybin-assisted therapy protocol for treatment-resistant depression based on Johns Hopkins research.",
        duration_weeks=12,
        total_sessions=8,
        evidence_sources=["Johns Hopkins 2020", "Imperial College London 2021"],
        created_by=admin_user.id
    )
    db_session.add(psilocybin_protocol)
    db_session.commit()
    db_session.refresh(psilocybin_protocol)

    # Add steps to psilocybin protocol
    psilocybin_steps = [
        ProtocolStep(
            protocol_id=psilocybin_protocol.id,
            sequence_order=1,
            step_type=StepType.SCREENING,
            title="Initial Psychiatric Evaluation",
            description="Comprehensive psychiatric assessment and medical history",
            duration_minutes=90,
            required_roles=["psychiatrist"],
        ),
        ProtocolStep(
            protocol_id=psilocybin_protocol.id,
            sequence_order=2,
            step_type=StepType.PREPARATION,
            title="Preparation Session",
            description="Build therapeutic alliance and set intentions",
            duration_minutes=60,
            required_roles=["therapist"],
        ),
        ProtocolStep(
            protocol_id=psilocybin_protocol.id,
            sequence_order=3,
            step_type=StepType.DOSING,
            title="Psilocybin Session",
            description="Supervised psilocybin dosing session (25mg)",
            duration_minutes=360,
            required_roles=["therapist", "medical_monitor"],
        ),
    ]
    db_session.add_all(psilocybin_steps)
    protocols.append(psilocybin_protocol)

    # MDMA Protocol
    mdma_protocol = Protocol(
        name="MDMA-Assisted Therapy for PTSD",
        version="2.0",
        status="active",
        therapy_type=TherapyType.MDMA,
        condition_treated="ptsd",
        evidence_level=EvidenceLevel.PHASE_3,
        overview="MAPS Phase 3 protocol for MDMA-assisted psychotherapy in treating PTSD.",
        duration_weeks=16,
        total_sessions=12,
        evidence_sources=["MAPS Phase 3 2021"],
        created_by=admin_user.id
    )
    db_session.add(mdma_protocol)
    protocols.append(mdma_protocol)

    # Ketamine Protocol
    ketamine_protocol = Protocol(
        name="Ketamine Infusion for Major Depressive Disorder",
        version="1.5",
        status="active",
        therapy_type=TherapyType.KETAMINE,
        condition_treated="major_depressive_disorder",
        evidence_level=EvidenceLevel.FDA_APPROVED,
        overview="FDA-approved ketamine infusion protocol for treatment-resistant depression.",
        duration_weeks=4,
        total_sessions=6,
        evidence_sources=["FDA 2019", "Yale 2020"],
        created_by=admin_user.id
    )
    db_session.add(ketamine_protocol)
    protocols.append(ketamine_protocol)

    # Draft Protocol (should not appear in public listings)
    draft_protocol = Protocol(
        name="Experimental LSD Protocol",
        version="0.1",
        status="draft",
        therapy_type=TherapyType.LSD,
        condition_treated="anxiety",
        evidence_level=EvidenceLevel.PHASE_1,
        overview="Experimental protocol under development",
        duration_weeks=8,
        total_sessions=4,
        created_by=admin_user.id
    )
    db_session.add(draft_protocol)

    db_session.commit()

    return protocols


def test_list_protocols(client: TestClient, sample_protocols):
    """Test listing all active protocols (public endpoint)."""
    response = client.get("/api/v1/protocols")

    assert response.status_code == 200
    data = response.json()

    # Should return paginated response
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

    # Should return 3 active protocols (draft excluded)
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # Verify protocol structure
    protocol = data["items"][0]
    assert "id" in protocol
    assert "name" in protocol
    assert "therapy_type" in protocol
    assert "condition_treated" in protocol
    assert "evidence_level" in protocol
    assert "overview" in protocol
    assert "duration_weeks" in protocol
    assert "total_sessions" in protocol


def test_list_protocols_filter_by_therapy_type(client: TestClient, sample_protocols):
    """Test filtering protocols by therapy type."""
    response = client.get("/api/v1/protocols?therapy_type=psilocybin")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["therapy_type"] == "psilocybin"
    assert data["items"][0]["name"] == "Psilocybin for Treatment-Resistant Depression"


def test_list_protocols_filter_by_condition(client: TestClient, sample_protocols):
    """Test filtering protocols by condition treated."""
    response = client.get("/api/v1/protocols?condition=ptsd")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["condition_treated"] == "ptsd"


def test_list_protocols_filter_by_evidence_level(client: TestClient, sample_protocols):
    """Test filtering protocols by evidence level."""
    response = client.get("/api/v1/protocols?evidence_level=fda_approved")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["evidence_level"] == "fda_approved"
    assert data["items"][0]["therapy_type"] == "ketamine"


def test_list_protocols_multiple_filters(client: TestClient, sample_protocols):
    """Test filtering protocols with multiple filters."""
    response = client.get("/api/v1/protocols?therapy_type=mdma&evidence_level=phase_3_trial")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["therapy_type"] == "mdma"
    assert data["items"][0]["evidence_level"] == "phase_3_trial"


def test_list_protocols_pagination(client: TestClient, sample_protocols):
    """Test protocol listing pagination."""
    # Get first page
    response = client.get("/api/v1/protocols?page=1&size=2")

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["size"] == 2
    assert len(data["items"]) == 2
    assert data["total"] == 3

    # Get second page
    response = client.get("/api/v1/protocols?page=2&size=2")

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 2
    assert len(data["items"]) == 1


def test_get_protocol_detail(client: TestClient, sample_protocols):
    """Test getting protocol details (public endpoint)."""
    protocol_id = sample_protocols[0].id

    response = client.get(f"/api/v1/protocols/{protocol_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == protocol_id
    assert data["name"] == "Psilocybin for Treatment-Resistant Depression"
    assert data["therapy_type"] == "psilocybin"
    assert data["condition_treated"] == "treatment_resistant_depression"
    assert data["evidence_level"] == "phase_3_trial"
    assert "overview" in data
    assert "duration_weeks" in data
    assert "total_sessions" in data
    assert "evidence_sources" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Should include step count
    assert "step_count" in data
    assert data["step_count"] == 3


def test_get_protocol_detail_not_found(client: TestClient):
    """Test getting non-existent protocol returns 404."""
    response = client.get("/api/v1/protocols/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_protocol_steps(client: TestClient, sample_protocols):
    """Test getting protocol steps (public endpoint)."""
    protocol_id = sample_protocols[0].id

    response = client.get(f"/api/v1/protocols/{protocol_id}/steps")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3

    # Verify steps are ordered by sequence
    assert data[0]["sequence_order"] == 1
    assert data[1]["sequence_order"] == 2
    assert data[2]["sequence_order"] == 3

    # Verify step structure
    step = data[0]
    assert "id" in step
    assert "sequence_order" in step
    assert "step_type" in step
    assert "title" in step
    assert "description" in step
    assert "duration_minutes" in step
    assert step["step_type"] == "screening"
    assert step["title"] == "Initial Psychiatric Evaluation"


def test_get_protocol_steps_not_found(client: TestClient):
    """Test getting steps for non-existent protocol returns 404."""
    response = client.get("/api/v1/protocols/99999/steps")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_protocol_steps_no_steps(client: TestClient, sample_protocols):
    """Test getting steps for protocol with no steps returns empty list."""
    # Use MDMA protocol which has no steps in fixtures
    protocol_id = sample_protocols[1].id

    response = client.get(f"/api/v1/protocols/{protocol_id}/steps")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0


def test_search_protocols(client: TestClient, sample_protocols):
    """Test searching protocols by name or description."""
    response = client.get("/api/v1/protocols/search?q=depression")

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data

    # Should match both psilocybin and ketamine protocols
    assert data["total"] >= 2

    # Verify results contain the search term
    for item in data["items"]:
        text = f"{item['name']} {item['overview']} {item['condition_treated']}".lower()
        assert "depression" in text


def test_search_protocols_by_therapy_type(client: TestClient, sample_protocols):
    """Test searching protocols by therapy type name."""
    response = client.get("/api/v1/protocols/search?q=mdma")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    assert any(item["therapy_type"] == "mdma" for item in data["items"])


def test_search_protocols_no_results(client: TestClient, sample_protocols):
    """Test searching protocols with no matches."""
    response = client.get("/api/v1/protocols/search?q=nonexistentprotocol")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_search_protocols_empty_query(client: TestClient, sample_protocols):
    """Test searching with empty query returns all protocols."""
    response = client.get("/api/v1/protocols/search?q=")

    assert response.status_code == 200
    data = response.json()

    # Should return all active protocols
    assert data["total"] == 3


def test_search_protocols_case_insensitive(client: TestClient, sample_protocols):
    """Test search is case insensitive."""
    response1 = client.get("/api/v1/protocols/search?q=PTSD")
    response2 = client.get("/api/v1/protocols/search?q=ptsd")

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    assert data1["total"] == data2["total"]
    assert data1["total"] >= 1
