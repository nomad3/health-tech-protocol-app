from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


class AuditService:
    """Service for managing audit logs and compliance tracking."""

    def __init__(self, db: Session):
        """Initialize the audit service with a database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def log_action(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: int,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log an action to the audit trail.

        Args:
            user_id: ID of the user performing the action (None for system actions)
            action: Action being performed (e.g., "view_patient_record", "update_treatment_plan")
            resource_type: Type of resource being accessed (e.g., "patient", "protocol")
            resource_id: ID of the resource
            changes: Optional dictionary containing before/after changes
            ip_address: Optional IP address of the request
            user_agent: Optional user agent string of the request

        Returns:
            The created AuditLog instance
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log

    def get_user_audit_trail(self, user_id: int, limit: int = 100) -> List[AuditLog]:
        """Get audit trail for a specific user.

        Args:
            user_id: ID of the user
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of AuditLog entries, ordered by timestamp descending (most recent first)
        """
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_resource_audit_trail(
        self, resource_type: str, resource_id: int, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit trail for a specific resource.

        Args:
            resource_type: Type of resource (e.g., "patient", "protocol")
            resource_id: ID of the resource
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of AuditLog entries, ordered by timestamp descending (most recent first)
        """
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_phi_access_logs(self, days: int = 30) -> List[AuditLog]:
        """Get PHI (Protected Health Information) access logs for HIPAA compliance.

        This retrieves all access logs for resources containing PHI within the specified
        time window. PHI resources include: patient, treatment_plan, session, treatment_session.

        Args:
            days: Number of days to look back (default: 30)

        Returns:
            List of AuditLog entries for PHI access, ordered by timestamp descending
        """
        # Define PHI resource types
        phi_resource_types = [
            "patient",
            "treatment_plan",
            "session",
            "treatment_session",
            "patient_profile",
        ]

        # Calculate the cutoff timestamp
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        # Query for PHI access logs
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.resource_type.in_(phi_resource_types),
                AuditLog.timestamp >= cutoff_time
            )
            .order_by(AuditLog.timestamp.desc())
            .all()
        )

    def log_ai_interaction(
        self,
        db: Session,
        user_id: int,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Log an AI interaction for audit and compliance.

        Args:
            db: Database session
            user_id: ID of the user making the AI request
            action: Type of AI action (e.g., "protocol_extraction", "patient_education_generation")
            input_data: Input data sent to AI (anonymized if needed)
            output_data: Summary of AI output (not full output due to size)
            metadata: Additional metadata (confidence scores, warnings, etc.)

        Returns:
            The created AuditLog instance
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=f"ai_{action}",
            resource_type="ai_interaction",
            resource_id=0,  # AI interactions don't have a specific resource ID
            changes={
                "input_summary": input_data,
                "output_summary": output_data,
                "metadata": metadata or {}
            }
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log
