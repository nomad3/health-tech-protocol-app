import pytest
import uuid
from datetime import datetime, timedelta
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.protocol import Protocol, TherapyType, EvidenceLevel
from app.models.profiles import TherapistProfile, Clinic, PatientProfile
from app.models.treatment import TreatmentPlan, TreatmentStatus
from app.core.security import hash_password, create_access_token


def get_unique_email(prefix="user"):
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
def patient_user(db_session):
    """Create a test patient user."""
    email = get_unique_email("patient")
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        role=UserRole.PATIENT
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create patient profile
    profile = PatientProfile(
        user_id=user.id,
        date_of_birth=datetime(1990, 1, 1).date(),
        medical_history={"conditions": []},
        medications=[],
        contraindications=[]
    )
    db_session.add(profile)
    db_session.commit()

    return user


@pytest.fixture
def therapist_user(db_session):
    """Create a test therapist user."""
    email = get_unique_email("therapist")
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        role=UserRole.THERAPIST
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def clinic(db_session):
    """Create a test clinic."""
    clinic = Clinic(
        name="Test Psychedelic Clinic",
        type="clinic",
        address="123 Main St, San Francisco, CA 94102",
        license_numbers=["CA-12345"],
        certifications=["MDMA", "Psilocybin"],
        protocols_enabled=["MDMA for PTSD", "Psilocybin for Depression"]
    )
    db_session.add(clinic)
    db_session.commit()
    db_session.refresh(clinic)
    return clinic


@pytest.fixture
def therapist_profile(db_session, therapist_user, clinic):
    """Create a test therapist profile."""
    profile = TherapistProfile(
        user_id=therapist_user.id,
        clinic_id=clinic.id,
        license_type="MD",
        license_number="CA12345678",
        license_state="CA",
        specialties=["Psychiatry", "Psychedelic Therapy"],
        certifications=["MDMA-Assisted Therapy"],
        protocols_certified=["MDMA for PTSD"]
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def protocol(db_session, therapist_user):
    """Create a test protocol."""
    protocol = Protocol(
        name="Psilocybin for Depression",
        version="1.0",
        status="active",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="treatment_resistant_depression",
        evidence_level=EvidenceLevel.PHASE_3,
        overview="Evidence-based psilocybin protocol for treatment-resistant depression",
        duration_weeks=12,
        total_sessions=8,
        created_by=therapist_user.id
    )
    db_session.add(protocol)
    db_session.commit()
    db_session.refresh(protocol)
    return protocol


@pytest.fixture
def treatment_plan(db_session, patient_user, therapist_user, clinic, protocol):
    """Create a test treatment plan."""
    plan = TreatmentPlan(
        patient_id=patient_user.id,
        therapist_id=therapist_user.id,
        clinic_id=clinic.id,
        protocol_id=protocol.id,
        protocol_version=protocol.version,
        status=TreatmentStatus.SCREENING,
        start_date=datetime.utcnow(),
        estimated_completion=datetime.utcnow() + timedelta(weeks=12)
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture
def patient_token(patient_user):
    """Create access token for patient user."""
    return create_access_token({"sub": patient_user.email, "role": patient_user.role.value})


@pytest.fixture
def therapist_token(therapist_user):
    """Create access token for therapist user."""
    return create_access_token({"sub": therapist_user.email, "role": therapist_user.role.value})


# Test: Provider Search
def test_search_providers_unauthenticated(client: TestClient):
    """Test provider search requires authentication."""
    response = client.get("/api/v1/patients/providers/search")
    assert response.status_code in [401, 403]  # FastAPI returns 403 when no credentials provided


def test_search_providers_authenticated(client: TestClient, patient_token, therapist_profile):
    """Test provider search with authentication."""
    response = client.get(
        "/api/v1/patients/providers/search",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check provider structure
    provider = data[0]
    assert "therapist" in provider
    assert "clinic" in provider
    assert provider["therapist"]["license_type"] == "MD"


def test_search_providers_with_filters(client: TestClient, patient_token, therapist_profile):
    """Test provider search with filters."""
    response = client.get(
        "/api/v1/patients/providers/search",
        params={"therapy_type": "psilocybin", "location": "CA"},
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# Test: Pre-screening
def test_pre_screening_unauthenticated(client: TestClient, protocol):
    """Test pre-screening requires authentication."""
    response = client.post(
        f"/api/v1/patients/protocols/{protocol.id}/pre-screen",
        json={"protocol_id": protocol.id, "responses": {"q1": "yes"}}
    )
    assert response.status_code in [401, 403]  # FastAPI returns 403 when no credentials provided


def test_pre_screening_authenticated(client: TestClient, patient_token, protocol):
    """Test pre-screening with authentication."""
    response = client.post(
        f"/api/v1/patients/protocols/{protocol.id}/pre-screen",
        json={
            "protocol_id": protocol.id,
            "responses": {
                "age": 25,
                "diagnosis": "depression",
                "medications": ["none"],
                "heart_condition": False
            }
        },
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_level" in data
    assert "eligible" in data
    assert "contraindications" in data
    assert "recommendations" in data
    assert data["risk_level"] in ["low", "medium", "high", "excluded"]


def test_pre_screening_protocol_not_found(client: TestClient, patient_token):
    """Test pre-screening with non-existent protocol."""
    response = client.post(
        "/api/v1/patients/protocols/99999/pre-screen",
        json={"protocol_id": 99999, "responses": {"q1": "yes"}},
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 404


# Test: Consultation Request
def test_consultation_request_unauthenticated(client: TestClient):
    """Test consultation request requires authentication."""
    response = client.post(
        "/api/v1/patients/consultation-request",
        json={"therapist_id": 1, "protocol_id": 1}
    )
    assert response.status_code in [401, 403]  # FastAPI returns 403 when no credentials provided


def test_consultation_request_authenticated(client: TestClient, patient_token, therapist_user, protocol):
    """Test consultation request with authentication."""
    response = client.post(
        "/api/v1/patients/consultation-request",
        json={
            "therapist_id": therapist_user.id,
            "protocol_id": protocol.id,
            "notes": "Looking for help with depression"
        },
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "consultation_id" in data


# Test: Get Treatment Plans
def test_get_treatment_plans_unauthenticated(client: TestClient):
    """Test getting treatment plans requires authentication."""
    response = client.get("/api/v1/patients/treatment-plans")
    assert response.status_code in [401, 403]  # FastAPI returns 403 when no credentials provided


def test_get_treatment_plans_authenticated(client: TestClient, patient_token, treatment_plan):
    """Test getting treatment plans with authentication."""
    response = client.get(
        "/api/v1/patients/treatment-plans",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check treatment plan structure
    plan = data[0]
    assert "id" in plan
    assert "protocol_name" in plan
    assert "therapist_name" in plan
    assert "status" in plan
    assert plan["status"] == "screening"


def test_get_treatment_plans_empty(client: TestClient, patient_token):
    """Test getting treatment plans when patient has none."""
    response = client.get(
        "/api/v1/patients/treatment-plans",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Should return all plans for this patient, might be 0 or more
    assert isinstance(data, list)


# Test: Get Treatment Plan Details
def test_get_treatment_plan_details_unauthenticated(client: TestClient, treatment_plan):
    """Test getting treatment plan details requires authentication."""
    response = client.get(f"/api/v1/patients/treatment-plans/{treatment_plan.id}")
    assert response.status_code in [401, 403]  # FastAPI returns 403 when no credentials provided


def test_get_treatment_plan_details_authenticated(client: TestClient, patient_token, treatment_plan):
    """Test getting treatment plan details with authentication."""
    response = client.get(
        f"/api/v1/patients/treatment-plans/{treatment_plan.id}",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == treatment_plan.id
    assert "protocol_name" in data
    assert "therapist_name" in data
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


def test_get_treatment_plan_details_not_found(client: TestClient, patient_token):
    """Test getting non-existent treatment plan."""
    response = client.get(
        "/api/v1/patients/treatment-plans/99999",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 404


def test_get_treatment_plan_details_unauthorized(client: TestClient, patient_token, treatment_plan, db_session):
    """Test getting another patient's treatment plan."""
    # Create another patient
    other_email = get_unique_email("other_patient")
    other_user = User(
        email=other_email,
        password_hash=hash_password("Password123!"),
        role=UserRole.PATIENT
    )
    db_session.add(other_user)
    db_session.commit()

    other_token = create_access_token({"sub": other_email, "role": "patient"})

    # Try to access original patient's treatment plan
    response = client.get(
        f"/api/v1/patients/treatment-plans/{treatment_plan.id}",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert response.status_code == 403


# Test: Sign Consent
def test_sign_consent_unauthenticated(client: TestClient, treatment_plan):
    """Test signing consent requires authentication."""
    response = client.post(
        f"/api/v1/patients/consent/{treatment_plan.id}",
        json={
            "treatment_plan_id": treatment_plan.id,
            "consent_text": "I agree to treatment",
            "signature": "John Doe",
            "agreed": True
        }
    )
    assert response.status_code in [401, 403]  # FastAPI returns 403 when no credentials provided


def test_sign_consent_authenticated(client: TestClient, patient_token, treatment_plan):
    """Test signing consent with authentication."""
    response = client.post(
        f"/api/v1/patients/consent/{treatment_plan.id}",
        json={
            "treatment_plan_id": treatment_plan.id,
            "consent_text": "I agree to participate in this treatment protocol...",
            "signature": "John Doe",
            "agreed": True
        },
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["treatment_plan_id"] == treatment_plan.id
    assert "signed_at" in data
    assert data["signature"] == "John Doe"


def test_sign_consent_must_agree(client: TestClient, patient_token, treatment_plan):
    """Test consent requires agreement."""
    response = client.post(
        f"/api/v1/patients/consent/{treatment_plan.id}",
        json={
            "treatment_plan_id": treatment_plan.id,
            "consent_text": "I agree to treatment",
            "signature": "John Doe",
            "agreed": False
        },
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert "must agree" in response.json()["detail"].lower()


def test_sign_consent_plan_not_found(client: TestClient, patient_token):
    """Test signing consent for non-existent plan."""
    response = client.post(
        "/api/v1/patients/consent/99999",
        json={
            "treatment_plan_id": 99999,
            "consent_text": "I agree",
            "signature": "John Doe",
            "agreed": True
        },
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 404
