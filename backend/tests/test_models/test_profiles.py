import pytest
from datetime import date
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.profiles import Clinic, TherapistProfile, PatientProfile
from app.database import SessionLocal


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def therapist_user(db_session: Session):
    """Create or get a therapist user and clean up any existing profile."""
    user = db_session.query(User).filter_by(email="therapist_profile_test@example.com").first()
    if not user:
        user = User(
            email="therapist_profile_test@example.com",
            password_hash="hashed_password",
            role=UserRole.THERAPIST,
        )
        db_session.add(user)
        db_session.commit()

    # Delete any existing therapist profile for this user
    existing_profile = db_session.query(TherapistProfile).filter_by(user_id=user.id).first()
    if existing_profile:
        db_session.delete(existing_profile)
        db_session.commit()

    return user


@pytest.fixture
def patient_user(db_session: Session):
    """Create or get a patient user and clean up any existing profile."""
    user = db_session.query(User).filter_by(email="patient_profile_test@example.com").first()
    if not user:
        user = User(
            email="patient_profile_test@example.com",
            password_hash="hashed_password",
            role=UserRole.PATIENT,
        )
        db_session.add(user)
        db_session.commit()

    # Delete any existing patient profile for this user
    existing_profile = db_session.query(PatientProfile).filter_by(user_id=user.id).first()
    if existing_profile:
        db_session.delete(existing_profile)
        db_session.commit()

    return user


@pytest.fixture
def clinic(db_session: Session):
    """Create a clinic for testing."""
    clinic = Clinic(
        name="Healing Center",
        type="clinic",
        address="123 Main St, San Francisco, CA 94102",
        license_numbers=["CA-12345", "DEA-67890"],
        certifications=["MAPS Certified", "Ketamine Clinic Network"],
        protocols_enabled=["psilocybin", "mdma", "ketamine"],
    )
    db_session.add(clinic)
    db_session.commit()
    db_session.refresh(clinic)
    return clinic


# Clinic Model Tests
def test_create_clinic(db_session: Session):
    """Test creating a clinic."""
    clinic = Clinic(
        name="Mind Medicine Clinic",
        type="clinic",
        address="456 Oak Ave, Portland, OR 97201",
        license_numbers=["OR-ABC123"],
        certifications=["State Medical Board Approved"],
        protocols_enabled=["psilocybin", "ketamine"],
    )
    db_session.add(clinic)
    db_session.commit()

    assert clinic.id is not None
    assert clinic.name == "Mind Medicine Clinic"
    assert clinic.type == "clinic"
    assert clinic.address == "456 Oak Ave, Portland, OR 97201"
    assert len(clinic.license_numbers) == 1
    assert "psilocybin" in clinic.protocols_enabled
    assert clinic.created_at is not None


def test_create_solo_practice(db_session: Session):
    """Test creating a solo practice."""
    practice = Clinic(
        name="Dr. Smith's Practice",
        type="solo_practice",
        address="789 Pine Rd, Austin, TX 78701",
        license_numbers=["TX-98765"],
        certifications=["Board Certified Psychiatrist"],
        protocols_enabled=["ketamine"],
    )
    db_session.add(practice)
    db_session.commit()

    assert practice.id is not None
    assert practice.type == "solo_practice"
    assert practice.name == "Dr. Smith's Practice"


def test_clinic_name_required(db_session: Session):
    """Test that clinic name is required."""
    clinic = Clinic(
        type="clinic",
        address="123 Main St",
        license_numbers=[],
        certifications=[],
        protocols_enabled=[],
    )
    db_session.add(clinic)
    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()


# TherapistProfile Model Tests
def test_create_therapist_profile(db_session: Session, therapist_user: User, clinic: Clinic):
    """Test creating a therapist profile."""
    profile = TherapistProfile(
        user_id=therapist_user.id,
        clinic_id=clinic.id,
        license_type="MD",
        license_number="CA-MD-12345",
        license_state="CA",
        specialties=["psychiatry", "psychedelic_therapy"],
        certifications=["MAPS Certified Therapist", "Board Certified Psychiatrist"],
        protocols_certified=["psilocybin", "mdma"],
    )
    db_session.add(profile)
    db_session.commit()

    assert profile.id is not None
    assert profile.user_id == therapist_user.id
    assert profile.clinic_id == clinic.id
    assert profile.license_type == "MD"
    assert profile.license_number == "CA-MD-12345"
    assert "psychiatry" in profile.specialties
    assert "psilocybin" in profile.protocols_certified
    assert profile.created_at is not None


def test_create_therapist_profile_without_clinic(db_session: Session, therapist_user: User):
    """Test creating a therapist profile without a clinic (solo practitioner)."""
    profile = TherapistProfile(
        user_id=therapist_user.id,
        clinic_id=None,
        license_type="LCSW",
        license_number="CA-LCSW-67890",
        license_state="CA",
        specialties=["trauma", "integration_therapy"],
        certifications=["LCSW"],
        protocols_certified=["ketamine"],
    )
    db_session.add(profile)
    db_session.commit()

    assert profile.id is not None
    assert profile.clinic_id is None
    assert profile.license_type == "LCSW"


def test_therapist_profile_user_id_unique(db_session: Session, therapist_user: User):
    """Test that user_id must be unique (one profile per therapist)."""
    profile1 = TherapistProfile(
        user_id=therapist_user.id,
        license_type="MD",
        license_number="ABC123",
        license_state="CA",
        specialties=[],
        certifications=[],
        protocols_certified=[],
    )
    profile2 = TherapistProfile(
        user_id=therapist_user.id,
        license_type="PhD",
        license_number="DEF456",
        license_state="NY",
        specialties=[],
        certifications=[],
        protocols_certified=[],
    )

    db_session.add(profile1)
    db_session.commit()

    db_session.add(profile2)
    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()


def test_therapist_profile_relationship_to_user(db_session: Session, therapist_user: User):
    """Test relationship between TherapistProfile and User."""
    profile = TherapistProfile(
        user_id=therapist_user.id,
        license_type="MD",
        license_number="ABC123",
        license_state="CA",
        specialties=[],
        certifications=[],
        protocols_certified=[],
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    assert profile.user.id == therapist_user.id
    assert profile.user.email == "therapist_profile_test@example.com"
    assert profile.user.role == UserRole.THERAPIST


def test_therapist_profile_relationship_to_clinic(db_session: Session, therapist_user: User, clinic: Clinic):
    """Test relationship between TherapistProfile and Clinic."""
    profile = TherapistProfile(
        user_id=therapist_user.id,
        clinic_id=clinic.id,
        license_type="MD",
        license_number="ABC123",
        license_state="CA",
        specialties=[],
        certifications=[],
        protocols_certified=[],
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    assert profile.clinic.id == clinic.id
    assert profile.clinic.name == "Healing Center"


def test_clinic_has_many_therapists(db_session: Session, clinic: Clinic):
    """Test that a clinic can have many therapists."""
    # Check if users already exist
    user1 = db_session.query(User).filter_by(email="therapist1_profile_test@example.com").first()
    if not user1:
        user1 = User(email="therapist1_profile_test@example.com", password_hash="hash", role=UserRole.THERAPIST)
        db_session.add(user1)

    user2 = db_session.query(User).filter_by(email="therapist2_profile_test@example.com").first()
    if not user2:
        user2 = User(email="therapist2_profile_test@example.com", password_hash="hash", role=UserRole.THERAPIST)
        db_session.add(user2)

    db_session.commit()

    # Clean up any existing profiles
    db_session.query(TherapistProfile).filter_by(user_id=user1.id).delete()
    db_session.query(TherapistProfile).filter_by(user_id=user2.id).delete()
    db_session.commit()

    profile1 = TherapistProfile(
        user_id=user1.id,
        clinic_id=clinic.id,
        license_type="MD",
        license_number="ABC123",
        license_state="CA",
        specialties=[],
        certifications=[],
        protocols_certified=[],
    )
    profile2 = TherapistProfile(
        user_id=user2.id,
        clinic_id=clinic.id,
        license_type="LCSW",
        license_number="DEF456",
        license_state="CA",
        specialties=[],
        certifications=[],
        protocols_certified=[],
    )
    db_session.add_all([profile1, profile2])
    db_session.commit()

    # Re-query clinic to get fresh data with relationships
    clinic = db_session.query(Clinic).filter_by(id=clinic.id).first()
    assert len(clinic.therapists) == 2
    assert any(t.license_type == "MD" for t in clinic.therapists)
    assert any(t.license_type == "LCSW" for t in clinic.therapists)


# PatientProfile Model Tests
def test_create_patient_profile(db_session: Session, patient_user: User):
    """Test creating a patient profile."""
    profile = PatientProfile(
        user_id=patient_user.id,
        date_of_birth=date(1990, 5, 15),
        medical_history={
            "conditions": ["depression", "anxiety"],
            "previous_treatments": ["SSRIs", "CBT"],
            "hospitalizations": [],
        },
        medications=[
            {"name": "Escitalopram", "dosage": "10mg", "frequency": "daily"},
            {"name": "Vitamin D", "dosage": "2000IU", "frequency": "daily"},
        ],
        contraindications=[],
    )
    db_session.add(profile)
    db_session.commit()

    assert profile.id is not None
    assert profile.user_id == patient_user.id
    assert profile.date_of_birth == date(1990, 5, 15)
    assert "depression" in profile.medical_history["conditions"]
    assert len(profile.medications) == 2
    assert profile.medications[0]["name"] == "Escitalopram"
    assert len(profile.contraindications) == 0
    assert profile.created_at is not None


def test_patient_profile_with_contraindications(db_session: Session, patient_user: User):
    """Test patient profile with detected contraindications."""
    profile = PatientProfile(
        user_id=patient_user.id,
        date_of_birth=date(1985, 3, 20),
        medical_history={
            "conditions": ["bipolar_disorder", "hypertension"],
            "previous_treatments": [],
            "hospitalizations": ["2020 - Manic episode"],
        },
        medications=[
            {"name": "Lithium", "dosage": "600mg", "frequency": "twice_daily"},
        ],
        contraindications=[
            {
                "type": "relative_contraindication",
                "condition": "bipolar_disorder",
                "severity": "warning",
                "notes": "Requires careful monitoring for manic episodes",
            }
        ],
    )
    db_session.add(profile)
    db_session.commit()

    assert profile.id is not None
    assert len(profile.contraindications) == 1
    assert profile.contraindications[0]["type"] == "relative_contraindication"
    assert profile.contraindications[0]["condition"] == "bipolar_disorder"


def test_patient_profile_user_id_unique(db_session: Session, patient_user: User):
    """Test that user_id must be unique (one profile per patient)."""
    profile1 = PatientProfile(
        user_id=patient_user.id,
        date_of_birth=date(1990, 1, 1),
        medical_history={},
        medications=[],
        contraindications=[],
    )
    profile2 = PatientProfile(
        user_id=patient_user.id,
        date_of_birth=date(1995, 1, 1),
        medical_history={},
        medications=[],
        contraindications=[],
    )

    db_session.add(profile1)
    db_session.commit()

    db_session.add(profile2)
    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()


def test_patient_profile_relationship_to_user(db_session: Session, patient_user: User):
    """Test relationship between PatientProfile and User."""
    profile = PatientProfile(
        user_id=patient_user.id,
        date_of_birth=date(1990, 5, 15),
        medical_history={},
        medications=[],
        contraindications=[],
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    assert profile.user.id == patient_user.id
    assert profile.user.email == "patient_profile_test@example.com"
    assert profile.user.role == UserRole.PATIENT


def test_patient_profile_date_of_birth_required(db_session: Session, patient_user: User):
    """Test that date_of_birth is required."""
    profile = PatientProfile(
        user_id=patient_user.id,
        medical_history={},
        medications=[],
        contraindications=[],
    )
    db_session.add(profile)
    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()
