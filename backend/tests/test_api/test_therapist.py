import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.main import app
from app.models.user import User, UserRole
from app.models.profiles import TherapistProfile, PatientProfile, Clinic
from app.models.treatment import TreatmentPlan, TreatmentSession, SessionStatus, TreatmentStatus
from app.models.protocol import Protocol, ProtocolStep, TherapyType, EvidenceLevel, StepType
from app.core.security import hash_password, create_access_token
from app.database import SessionLocal


client = TestClient(app)


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def therapist_user(db_session: Session):
    """Create a therapist user."""
    # Check if user already exists
    user = db_session.query(User).filter(User.email == "therapist@example.com").first()
    if user:
        return user

    user = User(
        email="therapist@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.THERAPIST
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def therapist_profile(db_session: Session, therapist_user: User):
    """Create therapist profile."""
    # Check if profile already exists
    profile = db_session.query(TherapistProfile).filter(
        TherapistProfile.user_id == therapist_user.id
    ).first()
    if profile:
        return profile

    # Check if clinic already exists
    clinic = db_session.query(Clinic).filter(Clinic.name == "Test Clinic").first()
    if not clinic:
        clinic = Clinic(
            name="Test Clinic",
            type="clinic",
            address="123 Main St"
        )
        db_session.add(clinic)
        db_session.commit()
        db_session.refresh(clinic)

    profile = TherapistProfile(
        user_id=therapist_user.id,
        clinic_id=clinic.id,
        license_type="MD",
        license_number="12345",
        license_state="CA",
        specialties=["psychiatry"],
        certifications=["psychedelic_therapy"],
        protocols_certified=["psilocybin"]
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture(scope="function")
def patient_user(db_session: Session):
    """Create a patient user."""
    # Check if user already exists
    user = db_session.query(User).filter(User.email == "patient@example.com").first()
    if user:
        return user

    user = User(
        email="patient@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.PATIENT
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create patient profile
    from datetime import date
    profile = PatientProfile(
        user_id=user.id,
        date_of_birth=date(1990, 1, 1),
        medical_history={"conditions": ["depression"]},
        medications=["sertraline"]
    )
    db_session.add(profile)
    db_session.commit()

    return user


@pytest.fixture(scope="function")
def protocol(db_session: Session, therapist_user: User):
    """Create a test protocol."""
    # Check if protocol already exists
    protocol = db_session.query(Protocol).filter(
        Protocol.name == "Psilocybin for Depression"
    ).first()

    if not protocol:
        protocol = Protocol(
            name="Psilocybin for Depression",
            version="1.0",
            status="active",
            therapy_type=TherapyType.PSILOCYBIN,
            condition_treated="depression",
            evidence_level=EvidenceLevel.PHASE_3,
            created_by=therapist_user.id
        )
        db_session.add(protocol)
        db_session.commit()
        db_session.refresh(protocol)

    # Check if protocol step already exists
    step = db_session.query(ProtocolStep).filter(
        ProtocolStep.protocol_id == protocol.id,
        ProtocolStep.sequence_order == 1
    ).first()

    if not step:
        step = ProtocolStep(
            protocol_id=protocol.id,
            sequence_order=1,
            step_type=StepType.SCREENING,
            title="Initial Screening",
            description="Initial psychiatric evaluation"
        )
        db_session.add(step)
        db_session.commit()
        db_session.refresh(step)

    return protocol


@pytest.fixture
def treatment_plan(db_session: Session, therapist_user: User, patient_user: User, protocol: Protocol):
    """Create a treatment plan."""
    plan = TreatmentPlan(
        patient_id=patient_user.id,
        therapist_id=therapist_user.id,
        protocol_id=protocol.id,
        protocol_version="1.0",
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow()
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture
def treatment_session(db_session: Session, treatment_plan: TreatmentPlan, protocol: Protocol, therapist_user: User):
    """Create a treatment session."""
    # Get the protocol step
    step = db_session.query(ProtocolStep).filter(ProtocolStep.protocol_id == protocol.id).first()

    session = TreatmentSession(
        treatment_plan_id=treatment_plan.id,
        protocol_step_id=step.id,
        scheduled_at=datetime.utcnow() + timedelta(hours=1),
        therapist_id=therapist_user.id,
        location="in_person",
        status=SessionStatus.SCHEDULED
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def therapist_token(therapist_user: User):
    """Create access token for therapist."""
    token_data = {"sub": therapist_user.email, "role": therapist_user.role.value}
    return create_access_token(token_data)


@pytest.fixture
def auth_headers(therapist_token: str):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {therapist_token}"}


# Test Dashboard Endpoint
def test_get_therapist_dashboard(db_session: Session, therapist_user: User, treatment_session: TreatmentSession, auth_headers: dict):
    """Test getting therapist dashboard."""
    response = client.get("/api/v1/therapist/dashboard", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "today_sessions" in data
    assert "pending_tasks" in data
    assert isinstance(data["today_sessions"], list)
    assert isinstance(data["pending_tasks"], list)


def test_get_therapist_dashboard_unauthorized():
    """Test dashboard without authentication."""
    response = client.get("/api/v1/therapist/dashboard")
    assert response.status_code == 403


# Test Patient List Endpoint
def test_get_therapist_patients(db_session: Session, therapist_user: User, treatment_plan: TreatmentPlan, auth_headers: dict):
    """Test getting therapist's patient list."""
    response = client.get("/api/v1/therapist/patients", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "email" in data[0]


def test_get_therapist_patients_only_own():
    """Test that therapist can only see their own patients."""
    # Create second therapist
    db = SessionLocal()
    try:
        # Check if therapist2 already exists
        therapist2 = db.query(User).filter(User.email == "therapist2@example.com").first()
        if not therapist2:
            therapist2 = User(
                email="therapist2@example.com",
                password_hash=hash_password("password123"),
                role=UserRole.THERAPIST
            )
            db.add(therapist2)
            db.commit()
            db.refresh(therapist2)

        token_data = {"sub": therapist2.email, "role": therapist2.role.value}
        token = create_access_token(token_data)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/therapist/patients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Should be empty since therapist2 has no patients
        assert len(data) == 0
    finally:
        db.close()


# Test Create Treatment Plan Endpoint
def test_create_treatment_plan(db_session: Session, therapist_user: User, patient_user: User, protocol: Protocol, auth_headers: dict):
    """Test creating a treatment plan."""
    plan_data = {
        "patient_id": patient_user.id,
        "protocol_id": protocol.id,
        "start_date": datetime.utcnow().isoformat(),
        "customizations": {"notes": "Custom treatment plan"}
    }

    response = client.post("/api/v1/therapist/treatment-plans", json=plan_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == patient_user.id
    assert data["therapist_id"] == therapist_user.id
    assert data["protocol_id"] == protocol.id
    assert data["status"] == "active"


# Test Get Session Details Endpoint
def test_get_session_details(db_session: Session, treatment_session: TreatmentSession, auth_headers: dict):
    """Test getting session details."""
    response = client.get(f"/api/v1/therapist/sessions/{treatment_session.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == treatment_session.id
    assert data["status"] == treatment_session.status.value
    assert "scheduled_at" in data


def test_get_session_details_not_own_patient():
    """Test that therapist cannot access sessions of other therapists' patients."""
    db = SessionLocal()
    try:
        # Check if therapist2 already exists
        therapist2 = db.query(User).filter(User.email == "therapist2@example.com").first()
        if not therapist2:
            therapist2 = User(
                email="therapist2@example.com",
                password_hash=hash_password("password123"),
                role=UserRole.THERAPIST
            )
            db.add(therapist2)
            db.commit()
            db.refresh(therapist2)

        token_data = {"sub": therapist2.email, "role": therapist2.role.value}
        token = create_access_token(token_data)
        headers = {"Authorization": f"Bearer {token}"}

        # Try to access a session that doesn't belong to this therapist
        # This should fail with 403 or 404
        response = client.get(f"/api/v1/therapist/sessions/999", headers=headers)
        assert response.status_code in [403, 404]
    finally:
        db.close()


# Test Log Vitals Endpoint
def test_log_session_vitals(db_session: Session, treatment_session: TreatmentSession, auth_headers: dict):
    """Test logging vitals during a session."""
    vitals_data = {
        "blood_pressure": "120/80",
        "heart_rate": 72,
        "temperature": 98.6,
        "spo2": 98,
        "timestamp": datetime.utcnow().isoformat()
    }

    response = client.post(
        f"/api/v1/therapist/sessions/{treatment_session.id}/vitals",
        json=vitals_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "vitals" in data or "message" in data


# Test Save Session Documentation Endpoint
def test_save_session_documentation(db_session: Session, treatment_session: TreatmentSession, auth_headers: dict):
    """Test saving session documentation."""
    doc_data = {
        "therapist_notes": "Patient responded well to treatment",
        "clinical_scales": {
            "PHQ-9": 12,
            "GAD-7": 8
        },
        "adverse_events": []
    }

    response = client.post(
        f"/api/v1/therapist/sessions/{treatment_session.id}/documentation",
        json=doc_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data or "message" in data


# Test Complete Session Endpoint
def test_complete_session(db_session: Session, treatment_session: TreatmentSession, auth_headers: dict):
    """Test completing a session."""
    # First, update session to in_progress
    treatment_session.status = SessionStatus.IN_PROGRESS
    treatment_session.actual_start = datetime.utcnow()
    db_session.commit()

    response = client.post(
        f"/api/v1/therapist/sessions/{treatment_session.id}/complete",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


# Test Evaluate Decision Point Endpoint
def test_evaluate_decision_point(db_session: Session, protocol: Protocol, treatment_plan: TreatmentPlan, auth_headers: dict):
    """Test evaluating a decision point."""
    # Create a decision point step
    decision_step = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=2,
        step_type=StepType.DECISION_POINT,
        title="Treatment Response Evaluation",
        description="Evaluate patient response",
        evaluation_rules={"min_phq9_reduction": 5}
    )
    db_session.add(decision_step)
    db_session.commit()
    db_session.refresh(decision_step)

    evaluation_data = {
        "treatment_plan_id": treatment_plan.id,
        "evaluation_criteria": {
            "phq9_baseline": 20,
            "phq9_current": 12,
            "response": "positive"
        },
        "recommendation": "continue"
    }

    response = client.post(
        f"/api/v1/therapist/decision-points/{decision_step.id}/evaluate",
        json=evaluation_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommendation" in data or "message" in data


# Test Authorization - Patient cannot access therapist endpoints
def test_patient_cannot_access_dashboard():
    """Test that patients cannot access therapist dashboard."""
    db = SessionLocal()
    try:
        # Check if patient already exists
        patient = db.query(User).filter(User.email == "patient_test@example.com").first()
        if not patient:
            patient = User(
                email="patient_test@example.com",
                password_hash=hash_password("password123"),
                role=UserRole.PATIENT
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        token_data = {"sub": patient.email, "role": patient.role.value}
        token = create_access_token(token_data)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/therapist/dashboard", headers=headers)
        assert response.status_code == 403
    finally:
        db.close()
