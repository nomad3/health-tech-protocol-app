import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.models.user import User, UserRole
from app.database import SessionLocal


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    import random
    email = f"test_{random.randint(1000, 9999)}@example.com"
    user = User(
        email=email,
        password_hash="hashed_password",
        role=UserRole.PATIENT,
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_create_audit_log(db_session: Session, test_user: User):
    """Test creating an audit log entry."""
    audit = AuditLog(
        user_id=test_user.id,
        action="view_patient_record",
        resource_type="patient",
        resource_id=123,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        changes={"field": "email", "old": "old@example.com", "new": "new@example.com"}
    )
    db_session.add(audit)
    db_session.commit()

    assert audit.id is not None
    assert audit.user_id == test_user.id
    assert audit.action == "view_patient_record"
    assert audit.resource_type == "patient"
    assert audit.resource_id == 123
    assert audit.ip_address == "192.168.1.1"
    assert audit.user_agent == "Mozilla/5.0"
    assert audit.changes["field"] == "email"
    assert audit.timestamp is not None
    assert audit.created_at is not None


def test_create_audit_log_system_action(db_session: Session):
    """Test creating audit log for system actions with null user_id."""
    audit = AuditLog(
        user_id=None,
        action="system_cleanup",
        resource_type="session",
        resource_id=456,
    )
    db_session.add(audit)
    db_session.commit()

    assert audit.id is not None
    assert audit.user_id is None
    assert audit.action == "system_cleanup"
    assert audit.resource_type == "session"
    assert audit.resource_id == 456


def test_audit_log_timestamp_auto_default(db_session: Session, test_user: User):
    """Test that timestamp is automatically set."""
    before = datetime.utcnow()
    audit = AuditLog(
        user_id=test_user.id,
        action="update_treatment_plan",
        resource_type="treatment_plan",
        resource_id=789,
    )
    db_session.add(audit)
    db_session.commit()
    after = datetime.utcnow()

    assert audit.timestamp is not None
    assert before <= audit.timestamp <= after


def test_audit_log_with_changes_json(db_session: Session, test_user: User):
    """Test audit log with JSON changes field."""
    changes = {
        "status": {"old": "draft", "new": "active"},
        "dosage": {"old": 10, "new": 15},
        "notes": {"old": None, "new": "Updated based on patient response"}
    }
    audit = AuditLog(
        user_id=test_user.id,
        action="update_protocol",
        resource_type="protocol",
        resource_id=5,
        changes=changes
    )
    db_session.add(audit)
    db_session.commit()

    assert audit.changes["status"]["old"] == "draft"
    assert audit.changes["status"]["new"] == "active"
    assert audit.changes["dosage"]["new"] == 15


def test_audit_log_nullable_fields(db_session: Session, test_user: User):
    """Test that optional fields can be null."""
    audit = AuditLog(
        user_id=test_user.id,
        action="delete_record",
        resource_type="note",
        resource_id=999,
        # ip_address, user_agent, and changes are None
    )
    db_session.add(audit)
    db_session.commit()

    assert audit.id is not None
    assert audit.ip_address is None
    assert audit.user_agent is None
    assert audit.changes is None


def test_multiple_audit_logs_ordering(db_session: Session, test_user: User):
    """Test querying multiple audit logs in order."""
    # Create multiple audit logs
    for i in range(5):
        audit = AuditLog(
            user_id=test_user.id,
            action=f"action_{i}",
            resource_type="test",
            resource_id=i,
        )
        db_session.add(audit)
    db_session.commit()

    # Query all logs ordered by timestamp
    logs = db_session.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

    assert len(logs) >= 5
    # Most recent should be first when ordered descending
    assert logs[0].action == "action_4"
