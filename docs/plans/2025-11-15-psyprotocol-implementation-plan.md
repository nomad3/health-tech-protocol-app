# PsyProtocol Platform - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete AI-powered psychedelic therapy protocol platform with patient journey, therapist workflows, protocol engine, and AI integration.

**Architecture:** FastAPI backend + PostgreSQL + Redis, React TypeScript frontend, Docker Compose deployment, Claude AI integration

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, SQLAlchemy, Alembic, Pydantic, pytest
- Frontend: React 18, TypeScript, Tailwind CSS, Vite, Vitest
- Database: PostgreSQL 15, Redis 7
- AI: Anthropic Claude API (SDK: anthropic-python)
- Auth: JWT (python-jose), Argon2 (passlib)
- Deployment: Docker, Docker Compose, Nginx, Let's Encrypt

**Important Principles:**
- TDD: Write failing test → Run test → Implement → Run test → Commit
- YAGNI: Only build what's needed for MVP
- DRY: Don't repeat yourself
- Frequent commits: After each passing test

---

## Phase 1: Project Foundation & Backend Core

### Task 1: Backend Project Structure

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Create: `backend/pytest.ini`

**Step 1: Create requirements.txt**

Create `backend/requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[argon2]==1.7.4
python-multipart==0.0.6
anthropic==0.7.7
redis==5.0.1
stripe==7.6.0
```

**Step 2: Create requirements-dev.txt**

Create `backend/requirements-dev.txt`:

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1
faker==20.1.0
black==23.11.0
ruff==0.1.6
```

**Step 3: Create .env.example**

Create `backend/.env.example`:

```bash
# Database
DATABASE_URL=postgresql://psyprotocol:password@localhost:5432/psyprotocol
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
STRIPE_SECRET_KEY=sk_test_your-key-here

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Step 4: Create config.py with Pydantic Settings**

Create `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str
    REDIS_URL: str

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Keys
    ANTHROPIC_API_KEY: str
    STRIPE_SECRET_KEY: str

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
```

**Step 5: Create minimal FastAPI app**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="PsyProtocol API",
    description="AI-powered psychedelic therapy protocol platform",
    version="1.0.0",
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "PsyProtocol API", "version": "1.0.0"}
```

**Step 6: Create Dockerfile**

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Step 7: Create .dockerignore**

Create `backend/.dockerignore`:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.pytest_cache/
.coverage
htmlcov/
.env
.env.local
```

**Step 8: Create pytest.ini**

Create `backend/pytest.ini`:

```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

**Step 9: Create .env file**

Run:

```bash
cd backend
cp .env.example .env
```

Expected: `.env` file created (user will add real API keys later)

**Step 10: Test backend starts**

Run:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Expected: Server starts on http://127.0.0.1:8000
Verify: `curl http://127.0.0.1:8000/health` returns `{"status":"healthy"}`

**Step 11: Commit**

```bash
git add backend/
git commit -m "feat(backend): initialize FastAPI project structure

- Add requirements and dev dependencies
- Create FastAPI app with health check endpoint
- Add config with Pydantic Settings
- Create Dockerfile for containerization
- Set up pytest configuration"
```

---

### Task 2: Database Setup & Connection

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/tests/test_database.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

**Step 1: Write failing test for database connection**

Create `backend/tests/test_database.py`:

```python
import pytest
from sqlalchemy import text
from app.database import engine, get_db


def test_database_connection():
    """Test that database connection works."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_db_session():
    """Test database session dependency."""
    db = next(get_db())
    assert db is not None
    db.close()
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd backend
pytest tests/test_database.py -v
```

Expected: FAIL (database.py doesn't exist)

**Step 3: Implement database.py**

Create `backend/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Database session dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 4: Create models __init__.py**

Create `backend/app/models/__init__.py`:

```python
from app.database import Base

# Import all models here for Alembic to discover
# from app.models.user import User
# from app.models.protocol import Protocol
```

**Step 5: Initialize Alembic**

Run:

```bash
cd backend
alembic init alembic
```

Expected: `alembic/` directory created

**Step 6: Configure Alembic env.py**

Edit `backend/alembic/env.py` - replace the entire file:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings
from app.models import Base

# Alembic Config object
config = context.config

# Set database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add model metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 7: Run test to verify it passes**

First, ensure PostgreSQL is running (via Docker or local):

```bash
docker run --name psyprotocol-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=psyprotocol -e POSTGRES_DB=psyprotocol -p 5432:5432 -d postgres:15-alpine
```

Then run tests:

```bash
cd backend
pytest tests/test_database.py -v
```

Expected: PASS

**Step 8: Commit**

```bash
git add backend/app/database.py backend/app/models/ backend/alembic/ backend/tests/test_database.py
git commit -m "feat(backend): add database connection and Alembic setup

- Create SQLAlchemy engine and session factory
- Add database session dependency for FastAPI
- Initialize Alembic for migrations
- Add tests for database connection"
```

---

### Task 3: User Model & Authentication Core

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/core/security.py`
- Create: `backend/tests/test_models/test_user.py`
- Create: `backend/tests/test_core/test_security.py`

**Step 1: Write failing test for User model**

Create `backend/tests/test_models/test_user.py`:

```python
import pytest
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.database import SessionLocal


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
    user1 = User(email="test@example.com", password_hash="hash", role=UserRole.PATIENT)
    user2 = User(email="test@example.com", password_hash="hash", role=UserRole.THERAPIST)

    db_session.add(user1)
    db_session.commit()

    db_session.add(user2)
    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd backend
pytest tests/test_models/test_user.py -v
```

Expected: FAIL (User model doesn't exist)

**Step 3: Implement User model**

Create `backend/app/models/user.py`:

```python
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, Enum):
    """User role enumeration."""
    PATIENT = "patient"
    THERAPIST = "therapist"
    CLINIC_ADMIN = "clinic_admin"
    MEDICAL_DIRECTOR = "medical_director"
    PLATFORM_ADMIN = "platform_admin"


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
```

**Step 4: Update models __init__.py**

Edit `backend/app/models/__init__.py`:

```python
from app.database import Base
from app.models.user import User, UserRole

__all__ = ["Base", "User", "UserRole"]
```

**Step 5: Create migration for users table**

Run:

```bash
cd backend
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

Expected: Migration created and applied

**Step 6: Run test to verify it passes**

Run:

```bash
cd backend
pytest tests/test_models/test_user.py -v
```

Expected: PASS

**Step 7: Write failing test for password hashing**

Create `backend/tests/test_core/test_security.py`:

```python
from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_hash_password():
    """Test password hashing."""
    password = "TestPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 50  # Argon2 hashes are long


def test_verify_password():
    """Test password verification."""
    password = "TestPassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    """Test JWT token creation."""
    payload = {"sub": "user@example.com", "role": "patient"}
    token = create_access_token(payload)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 50


def test_decode_token():
    """Test JWT token decoding."""
    payload = {"sub": "user@example.com", "role": "patient"}
    token = create_access_token(payload)

    decoded = decode_token(token)
    assert decoded["sub"] == "user@example.com"
    assert decoded["role"] == "patient"
```

**Step 8: Run test to verify it fails**

Run:

```bash
cd backend
pytest tests/test_core/test_security.py -v
```

Expected: FAIL (security.py doesn't exist)

**Step 9: Implement security.py**

Create `backend/app/core/security.py`:

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
```

**Step 10: Run test to verify it passes**

Run:

```bash
cd backend
pytest tests/test_core/test_security.py -v
```

Expected: PASS

**Step 11: Commit**

```bash
git add backend/app/models/user.py backend/app/core/security.py backend/tests/
git commit -m "feat(backend): add User model and authentication core

- Create User model with role-based access control
- Add Argon2 password hashing
- Implement JWT token creation and validation
- Add comprehensive tests for auth core"
```

---

## Phase 2: Protocol Models & Engine

### Task 4: Protocol Core Models

**Files:**
- Create: `backend/app/models/protocol.py`
- Create: `backend/app/schemas/protocol.py`
- Create: `backend/tests/test_models/test_protocol.py`

**Step 1: Write failing test for Protocol model**

Create `backend/tests/test_models/test_protocol.py`:

```python
import pytest
from sqlalchemy.orm import Session
from app.models.protocol import Protocol, ProtocolStep, StepType, TherapyType, EvidenceLevel
from app.database import SessionLocal


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def test_create_protocol(db_session: Session):
    """Test creating a protocol."""
    protocol = Protocol(
        name="Psilocybin for Depression",
        version="1.0",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="treatment_resistant_depression",
        evidence_level=EvidenceLevel.PHASE_3,
        created_by=1,
    )
    db_session.add(protocol)
    db_session.commit()

    assert protocol.id is not None
    assert protocol.name == "Psilocybin for Depression"
    assert protocol.status == "draft"
    assert protocol.created_at is not None


def test_create_protocol_step(db_session: Session):
    """Test creating protocol steps."""
    protocol = Protocol(
        name="Test Protocol",
        version="1.0",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="depression",
        evidence_level=EvidenceLevel.PHASE_3,
        created_by=1,
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


def test_protocol_steps_relationship(db_session: Session):
    """Test protocol-steps relationship."""
    protocol = Protocol(
        name="Test Protocol",
        version="1.0",
        therapy_type=TherapyType.MDMA,
        condition_treated="ptsd",
        evidence_level=EvidenceLevel.FDA_APPROVED,
        created_by=1,
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
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd backend
pytest tests/test_models/test_protocol.py -v
```

Expected: FAIL (protocol.py doesn't exist)

**Step 3: Implement Protocol models**

Create `backend/app/models/protocol.py`:

```python
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class TherapyType(str, Enum):
    """Therapy type enumeration."""
    PSILOCYBIN = "psilocybin"
    MDMA = "mdma"
    KETAMINE = "ketamine"
    LSD = "lsd"
    IBOGAINE = "ibogaine"
    OTHER = "other"


class EvidenceLevel(str, Enum):
    """Evidence level enumeration."""
    FDA_APPROVED = "fda_approved"
    PHASE_3 = "phase_3_trial"
    PHASE_2 = "phase_2_trial"
    PHASE_1 = "phase_1_trial"
    PRECLINICAL = "preclinical"
    CLINICAL_PRACTICE = "clinical_practice"


class StepType(str, Enum):
    """Protocol step type enumeration."""
    SCREENING = "screening"
    PREPARATION = "preparation"
    DOSING = "dosing"
    INTEGRATION = "integration"
    DECISION_POINT = "decision_point"
    FOLLOWUP = "followup"


class Protocol(Base):
    """Protocol model representing treatment protocols."""

    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft, active, archived
    therapy_type = Column(SQLEnum(TherapyType), nullable=False)
    condition_treated = Column(String(255), nullable=False)
    evidence_level = Column(SQLEnum(EvidenceLevel), nullable=False)
    overview = Column(Text)
    duration_weeks = Column(Integer)
    total_sessions = Column(Integer)
    evidence_sources = Column(JSON)  # Array of evidence sources
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    steps = relationship("ProtocolStep", back_populates="protocol", order_by="ProtocolStep.sequence_order")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Protocol(id={self.id}, name={self.name}, version={self.version})>"


class ProtocolStep(Base):
    """Protocol step model representing individual steps in a protocol."""

    __tablename__ = "protocol_steps"

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    step_type = Column(SQLEnum(StepType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer)
    required_roles = Column(JSON)  # Array of required roles
    documentation_template_id = Column(Integer, nullable=True)

    # Decision point specific fields
    evaluation_rules = Column(JSON)  # Decision logic
    branch_outcomes = Column(JSON)  # Possible outcomes

    # Clinical scales and monitoring
    clinical_scales = Column(JSON)  # Array of scale names
    vitals_monitoring = Column(JSON)  # Vitals monitoring config

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    protocol = relationship("Protocol", back_populates="steps")
    safety_checks = relationship("SafetyCheck", back_populates="protocol_step")

    def __repr__(self):
        return f"<ProtocolStep(id={self.id}, title={self.title}, type={self.step_type})>"


class SafetyCheck(Base):
    """Safety check model for contraindications and risk factors."""

    __tablename__ = "safety_checks"

    id = Column(Integer, primary_key=True, index=True)
    protocol_step_id = Column(Integer, ForeignKey("protocol_steps.id"), nullable=False)
    check_type = Column(String(100), nullable=False)  # absolute_contraindication, relative_contraindication, risk_factor
    condition = Column(JSON, nullable=False)  # Condition definition
    severity = Column(String(50), nullable=False)  # blocking, warning, info
    override_allowed = Column(String(10), default="false", nullable=False)
    override_requirements = Column(JSON)  # Requirements for override
    evidence_source = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    protocol_step = relationship("ProtocolStep", back_populates="safety_checks")

    def __repr__(self):
        return f"<SafetyCheck(id={self.id}, type={self.check_type}, severity={self.severity})>"
```

**Step 4: Update models __init__.py**

Edit `backend/app/models/__init__.py`:

```python
from app.database import Base
from app.models.user import User, UserRole
from app.models.protocol import (
    Protocol,
    ProtocolStep,
    SafetyCheck,
    TherapyType,
    EvidenceLevel,
    StepType,
)

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Protocol",
    "ProtocolStep",
    "SafetyCheck",
    "TherapyType",
    "EvidenceLevel",
    "StepType",
]
```

**Step 5: Create migration**

Run:

```bash
cd backend
alembic revision --autogenerate -m "create protocol tables"
alembic upgrade head
```

Expected: Migration created and applied

**Step 6: Run test to verify it passes**

Run:

```bash
cd backend
pytest tests/test_models/test_protocol.py -v
```

Expected: PASS

**Step 7: Commit**

```bash
git add backend/app/models/protocol.py backend/tests/test_models/test_protocol.py
git commit -m "feat(backend): add Protocol, ProtocolStep, and SafetyCheck models

- Create Protocol model with therapy types and evidence levels
- Add ProtocolStep model with decision point support
- Implement SafetyCheck model for contraindications
- Add comprehensive tests for protocol models"
```

---

*[Due to length, I'll continue with more condensed task summaries. The full plan would include 40+ tasks following this same pattern.]*

### Task 5: Treatment Plan & Session Models

**Creates:** TreatmentPlan, TreatmentSession, SessionDocumentation models
**Tests:** Comprehensive model tests
**Migration:** Treatment tables

### Task 6: Patient & Therapist Profile Models

**Creates:** PatientProfile, TherapistProfile, Clinic models
**Tests:** Profile relationship tests
**Migration:** Profile tables

### Task 7: Audit Log & Compliance

**Creates:** AuditLog model and service
**Tests:** Audit logging tests
**Migration:** Audit log table

---

## Phase 3: API Endpoints

### Task 8: Authentication Endpoints

**Creates:** `/api/v1/auth/register`, `/login`, `/refresh`, `/logout`
**Tests:** Auth flow integration tests
**Security:** JWT validation middleware

### Task 9: Protocol CRUD Endpoints

**Creates:** Protocol browsing, detail, search endpoints
**Tests:** Protocol API tests
**Permissions:** Public read, admin write

### Task 10: Admin Protocol Creation

**Creates:** Protocol builder endpoints
**Tests:** Full protocol creation workflow
**Validation:** Pydantic schemas

### Task 11: Patient Journey Endpoints

**Creates:** Provider search, screening, treatment plan endpoints
**Tests:** Patient flow integration tests
**Business logic:** Matching algorithm

### Task 12: Therapist Workflow Endpoints

**Creates:** Dashboard, session docs, vitals logging
**Tests:** Therapist API integration tests
**Real-time:** Redis caching for active sessions

---

## Phase 4: Protocol Engine

### Task 13: Decision Point Evaluator

**Creates:** `app/services/protocol_engine.py` - decision logic
**Tests:** Complex decision tree tests
**Algorithm:** Multi-factor evaluation

### Task 14: Safety Check Service

**Creates:** `app/services/safety_service.py` - contraindication checking
**Tests:** Safety rule evaluation tests
**Business logic:** Risk scoring algorithm

### Task 15: Protocol Execution Service

**Creates:** Step progression, status tracking
**Tests:** Full protocol execution tests
**State machine:** Treatment plan status management

---

## Phase 5: AI Integration

### Task 16: Claude Client Setup

**Creates:** `app/services/ai_service.py` - Anthropic client
**Tests:** Mock AI response tests
**Error handling:** Rate limiting, fallbacks

### Task 17: Protocol Extraction Feature

**Creates:** PDF parsing + AI extraction
**Tests:** Protocol extraction tests
**Prompts:** `app/utils/ai_prompts.py`

### Task 18: Patient Education Generator

**Creates:** Personalized guide generation
**Tests:** Education content tests
**Caching:** Redis cache for generated content

### Task 19: Clinical Decision Support

**Creates:** Real-time decision support
**Tests:** Decision support tests
**Safety:** Audit all AI interactions

---

## Phase 6: Frontend Foundation

### Task 20: React Project Setup

**Creates:** Vite + React + TypeScript + Tailwind
**Tests:** Vitest configuration
**Structure:** Component folders

### Task 21: Design System Components

**Creates:** Button, Card, Modal, Badge, Input components
**Tests:** Component unit tests
**Storybook:** Component documentation

### Task 22: API Client & State Management

**Creates:** Axios client, Redux Toolkit slices
**Tests:** API client tests
**Auth:** Token management

---

## Phase 7: Frontend Features

### Task 23: Auth Pages

**Creates:** Login, Register, Password Reset pages
**Tests:** Auth flow E2E tests
**Forms:** React Hook Form + validation

### Task 24: Protocol Browser (Patient)

**Creates:** Protocol cards, search, filters
**Tests:** Protocol browsing tests
**UI:** Responsive grid layout

### Task 25: Therapist Dashboard

**Creates:** Schedule, patient list, quick actions
**Tests:** Dashboard tests
**Real-time:** Auto-refresh pending tasks

### Task 26: Session Documentation UI

**Creates:** Vitals logger, notes editor, clinical scales
**Tests:** Session documentation tests
**UX:** Auto-save drafts

### Task 27: Protocol Builder (Admin)

**Creates:** Drag-drop protocol builder
**Tests:** Protocol creation tests
**AI:** Integration with extraction feature

---

## Phase 8: Deployment

### Task 28: Docker Compose Setup

**Creates:** `docker-compose.yml`, `docker-compose.prod.yml`
**Tests:** Local multi-container deployment
**Services:** Backend, Frontend, PostgreSQL, Redis, Nginx

### Task 29: Nginx Configuration

**Creates:** `nginx/nginx.conf` with reverse proxy
**Tests:** Proxy routing tests
**SSL:** Let's Encrypt config

### Task 30: Deploy Script

**Creates:** `deploy.sh` - automated deployment
**Tests:** Dry-run deployment
**Automation:** Full VM setup

### Task 31: Database Seeding

**Creates:** Seed data for 3 example protocols
**Tests:** Seed script tests
**Data:** Psilocybin, MDMA, Ketamine protocols

---

## Phase 9: Testing & Quality

### Task 32: Integration Tests

**Creates:** Full API integration test suite
**Coverage:** >80% code coverage
**CI:** GitHub Actions workflow

### Task 33: E2E Tests

**Creates:** Playwright tests for critical flows
**Scenarios:** Patient journey, therapist workflow
**Automation:** Automated E2E in CI

### Task 34: Security Testing

**Creates:** Security test suite
**Tests:** SQL injection, XSS, CSRF
**Audit:** OWASP top 10

### Task 35: Performance Testing

**Creates:** Load tests with Locust
**Benchmarks:** API response times
**Optimization:** Query optimization

---

## Phase 10: Documentation

### Task 36: API Documentation

**Creates:** OpenAPI/Swagger docs
**Auto-generated:** FastAPI automatic docs
**Examples:** Request/response samples

### Task 37: User Documentation

**Creates:** User guides for each role
**Formats:** Markdown + screenshots
**Deployment:** Docs site

### Task 38: Developer Documentation

**Creates:** Architecture docs, setup guide
**Formats:** README, CONTRIBUTING.md
**Onboarding:** New developer guide

---

## Phase 11: Final Polish

### Task 39: Error Handling & Logging

**Improves:** Consistent error responses
**Logging:** Structured logging
**Monitoring:** Error tracking setup

### Task 40: Performance Optimization

**Optimizes:** Database queries, Redis caching
**Frontend:** Code splitting, lazy loading
**Benchmarks:** Load testing validation

### Task 41: Final Security Hardening

**Hardens:** Rate limiting, CORS, CSP headers
**Audit:** Security checklist completion
**Compliance:** HIPAA compliance review

### Task 42: Production Deployment

**Deploys:** To GCP VM
**Tests:** Production smoke tests
**Monitoring:** Set up alerts

---

## Appendix: Example Protocol Seed Data

The implementation should include JSON files for:

1. **Psilocybin for Depression** (10 steps with decision points)
2. **MDMA for PTSD** (15 steps MAPS protocol)
3. **Ketamine Infusion** (6-session protocol)

Each protocol includes:
- Full step definitions
- Safety checks
- Decision point rules
- Evidence sources

---

**End of Implementation Plan**

This plan contains **42 major tasks**, each broken into **5-10 micro-steps** following TDD principles. Total estimated: **300-400 individual commits** over 2-3 months with a small team using AI assistance.
