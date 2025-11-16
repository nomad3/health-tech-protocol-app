import pytest
import uuid
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, SessionLocal, Base, engine
from app.models.user import User, UserRole
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


def test_register_user(client: TestClient, db_session: Session):
    """Test user registration endpoint."""
    unique_email = get_unique_email("patient")

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": "SecurePassword123!",
            "role": "patient"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == unique_email
    assert data["role"] == "patient"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data

    # Verify user was created in database
    user = db_session.query(User).filter(User.email == unique_email).first()
    assert user is not None
    assert user.role == UserRole.PATIENT


def test_register_user_duplicate_email(client: TestClient, db_session: Session):
    """Test registration with duplicate email fails."""
    email = get_unique_email("duplicate")

    # Create first user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "role": "patient"
        }
    )

    # Try to create second user with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "DifferentPassword123!",
            "role": "therapist"
        }
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_role(client: TestClient):
    """Test registration with invalid role fails."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123!",
            "role": "invalid_role"
        }
    )

    assert response.status_code == 422  # Validation error


def test_login_success(client: TestClient, db_session: Session):
    """Test login with correct credentials."""
    email = get_unique_email("login")

    # Create user first
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        role=UserRole.THERAPIST
    )
    db_session.add(user)
    db_session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 50
    assert len(data["refresh_token"]) > 50


def test_login_wrong_password(client: TestClient, db_session: Session):
    """Test login with wrong password fails."""
    email = get_unique_email("wrong")

    # Create user
    user = User(
        email=email,
        password_hash=hash_password("CorrectPassword123!"),
        role=UserRole.PATIENT
    )
    db_session.add(user)
    db_session.commit()

    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user fails."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "Password123!"
        }
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_refresh_token(client: TestClient, db_session: Session):
    """Test token refresh."""
    email = get_unique_email("refresh")

    # Create user and login
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        role=UserRole.THERAPIST
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!"
        }
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_invalid_token(client: TestClient):
    """Test refresh with invalid token fails."""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"}
    )

    assert response.status_code == 401


def test_get_current_user(client: TestClient, db_session: Session):
    """Test getting current user info with valid token."""
    email = get_unique_email("current")

    # Create user and login
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        role=UserRole.CLINIC_ADMIN
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!"
        }
    )
    access_token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["role"] == "clinic_admin"
    assert "id" in data
    assert "created_at" in data


def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token fails."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )

    assert response.status_code == 401


def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without token fails."""
    response = client.get("/api/v1/auth/me")

    # FastAPI's HTTPBearer returns 403 when no Authorization header is provided
    assert response.status_code == 403


def test_protected_endpoint_with_valid_token(client: TestClient, db_session: Session):
    """Test accessing protected endpoint with valid token."""
    email = get_unique_email("protected")

    # Create user and login
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        role=UserRole.PATIENT
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!"
        }
    )
    access_token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200


def test_access_token_expiry_format(client: TestClient, db_session: Session):
    """Test that tokens contain expiry information."""
    email = get_unique_email("expiry")

    # Create user and login
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        role=UserRole.PATIENT
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify we can decode tokens (they're valid JWTs)
    from app.core.security import decode_token
    access_payload = decode_token(data["access_token"])
    refresh_payload = decode_token(data["refresh_token"])

    assert "exp" in access_payload
    assert "type" in access_payload
    assert access_payload["type"] == "access"
    assert "exp" in refresh_payload
    assert refresh_payload["type"] == "refresh"
