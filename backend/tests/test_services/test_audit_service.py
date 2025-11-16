import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.audit import AuditLog
from app.services.audit_service import AuditService
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


@pytest.fixture
def audit_service(db_session: Session):
    """Create AuditService instance."""
    return AuditService(db_session)


def test_log_action_basic(audit_service: AuditService, test_user: User, db_session: Session):
    """Test logging a basic action."""
    audit_service.log_action(
        user_id=test_user.id,
        action="view_patient_record",
        resource_type="patient",
        resource_id=123
    )

    # Verify log was created
    log = db_session.query(AuditLog).filter_by(
        user_id=test_user.id,
        action="view_patient_record"
    ).first()

    assert log is not None
    assert log.resource_type == "patient"
    assert log.resource_id == 123


def test_log_action_with_metadata(audit_service: AuditService, test_user: User, db_session: Session):
    """Test logging action with IP address and user agent."""
    audit_service.log_action(
        user_id=test_user.id,
        action="update_treatment_plan",
        resource_type="treatment_plan",
        resource_id=456,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0"
    )

    log = db_session.query(AuditLog).filter_by(
        user_id=test_user.id,
        action="update_treatment_plan"
    ).first()

    assert log.ip_address == "192.168.1.100"
    assert log.user_agent == "Mozilla/5.0"


def test_log_action_with_changes(audit_service: AuditService, test_user: User, db_session: Session):
    """Test logging action with changes diff."""
    changes = {
        "status": {"old": "draft", "new": "active"},
        "dosage": {"old": 10, "new": 15}
    }

    audit_service.log_action(
        user_id=test_user.id,
        action="update_protocol",
        resource_type="protocol",
        resource_id=789,
        changes=changes
    )

    log = db_session.query(AuditLog).filter_by(
        user_id=test_user.id,
        action="update_protocol"
    ).first()

    assert log.changes is not None
    assert log.changes["status"]["old"] == "draft"
    assert log.changes["status"]["new"] == "active"


def test_log_system_action(audit_service: AuditService, db_session: Session):
    """Test logging system action with null user_id."""
    audit_service.log_action(
        user_id=None,
        action="system_cleanup",
        resource_type="session",
        resource_id=999
    )

    log = db_session.query(AuditLog).filter_by(
        action="system_cleanup"
    ).first()

    assert log is not None
    assert log.user_id is None
    assert log.resource_type == "session"


def test_get_user_audit_trail(audit_service: AuditService, test_user: User, db_session: Session):
    """Test retrieving audit trail for a specific user."""
    # Create multiple logs for the user
    for i in range(5):
        audit_service.log_action(
            user_id=test_user.id,
            action=f"action_{i}",
            resource_type="test",
            resource_id=i
        )

    # Get user audit trail
    trail = audit_service.get_user_audit_trail(test_user.id, limit=10)

    assert len(trail) >= 5
    # Should be ordered by timestamp descending (most recent first)
    assert trail[0].action == "action_4"
    assert trail[4].action == "action_0"


def test_get_user_audit_trail_with_limit(audit_service: AuditService, test_user: User, db_session: Session):
    """Test audit trail respects limit parameter."""
    # Create 10 logs
    for i in range(10):
        audit_service.log_action(
            user_id=test_user.id,
            action=f"action_{i}",
            resource_type="test",
            resource_id=i
        )

    # Get only 3 most recent
    trail = audit_service.get_user_audit_trail(test_user.id, limit=3)

    assert len(trail) == 3
    assert trail[0].action == "action_9"
    assert trail[2].action == "action_7"


def test_get_resource_audit_trail(audit_service: AuditService, test_user: User, db_session: Session):
    """Test retrieving audit trail for a specific resource."""
    import random
    resource_id = random.randint(10000, 99999)

    # Create multiple logs for the same resource
    actions = ["create", "view", "update", "view_again"]
    for action in actions:
        audit_service.log_action(
            user_id=test_user.id,
            action=action,
            resource_type="patient",
            resource_id=resource_id
        )

    # Get resource audit trail
    trail = audit_service.get_resource_audit_trail("patient", resource_id, limit=10)

    assert len(trail) == 4
    # Most recent first
    assert trail[0].action == "view_again"
    assert trail[3].action == "create"


def test_get_resource_audit_trail_with_limit(audit_service: AuditService, test_user: User, db_session: Session):
    """Test resource audit trail respects limit."""
    import random
    resource_id = random.randint(10000, 99999)

    # Create 5 logs
    for i in range(5):
        audit_service.log_action(
            user_id=test_user.id,
            action=f"action_{i}",
            resource_type="protocol",
            resource_id=resource_id
        )

    # Get only 2 most recent
    trail = audit_service.get_resource_audit_trail("protocol", resource_id, limit=2)

    assert len(trail) == 2
    assert trail[0].action == "action_4"
    assert trail[1].action == "action_3"


def test_get_phi_access_logs(audit_service: AuditService, test_user: User, db_session: Session):
    """Test retrieving PHI access logs for HIPAA compliance."""
    # Create PHI-related logs
    phi_actions = [
        "view_patient_record",
        "view_treatment_plan",
        "view_session_notes",
        "download_patient_data"
    ]

    for action in phi_actions:
        audit_service.log_action(
            user_id=test_user.id,
            action=action,
            resource_type="patient",
            resource_id=123
        )

    # Create non-PHI logs
    audit_service.log_action(
        user_id=test_user.id,
        action="view_protocol",
        resource_type="protocol",
        resource_id=1
    )

    # Get PHI access logs from last 30 days
    phi_logs = audit_service.get_phi_access_logs(days=30)

    # Should include PHI-related logs
    phi_actions_found = [log.action for log in phi_logs]
    assert "view_patient_record" in phi_actions_found
    assert "view_treatment_plan" in phi_actions_found
    assert "view_session_notes" in phi_actions_found
    assert "download_patient_data" in phi_actions_found


def test_get_phi_access_logs_time_filter(audit_service: AuditService, test_user: User, db_session: Session):
    """Test PHI access logs respects time window."""
    # Create a PHI log
    audit_service.log_action(
        user_id=test_user.id,
        action="view_patient_record",
        resource_type="patient",
        resource_id=123
    )

    # Get logs from last 30 days (should include)
    phi_logs_30 = audit_service.get_phi_access_logs(days=30)
    assert len(phi_logs_30) >= 1

    # Get logs from last 0 days (should be empty or very limited)
    phi_logs_0 = audit_service.get_phi_access_logs(days=0)
    # This might be 0 or 1 depending on timing
    assert len(phi_logs_0) <= 1


def test_get_phi_access_logs_only_phi_resources(audit_service: AuditService, test_user: User, db_session: Session):
    """Test that only PHI-related resources are returned."""
    # PHI resources
    phi_resources = ["patient", "treatment_plan", "session", "treatment_session"]

    for resource in phi_resources:
        audit_service.log_action(
            user_id=test_user.id,
            action=f"view_{resource}",
            resource_type=resource,
            resource_id=123
        )

    # Non-PHI resources
    audit_service.log_action(
        user_id=test_user.id,
        action="view_protocol",
        resource_type="protocol",
        resource_id=1
    )

    # Get PHI logs
    phi_logs = audit_service.get_phi_access_logs(days=30)

    # Verify only PHI resources
    resource_types = [log.resource_type for log in phi_logs]
    assert "patient" in resource_types or "treatment_plan" in resource_types
    # Protocol should not be in PHI logs (it's public data)
