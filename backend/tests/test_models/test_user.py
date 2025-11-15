import pytest
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.database import SessionLocal, engine
from app.models import Base


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def test_create_user(db_session: Session):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.PATIENT,
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.PATIENT
    assert user.is_active is True
    assert user.created_at is not None


def test_user_email_unique(db_session: Session):
    """Test that email must be unique."""
    user1 = User(email="unique@example.com", password_hash="hash", role=UserRole.PATIENT)
    user2 = User(email="unique@example.com", password_hash="hash", role=UserRole.THERAPIST)

    db_session.add(user1)
    db_session.commit()

    db_session.add(user2)
    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()
