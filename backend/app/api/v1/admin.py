from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.protocol import Protocol, ProtocolStep, SafetyCheck
from app.schemas.protocol import (
    ProtocolCreate,
    ProtocolUpdate,
    ProtocolStepCreate,
    ProtocolStepUpdate,
    SafetyCheckCreate,
    ProtocolPublish,
    ProtocolResponse,
    ProtocolStepResponse,
    SafetyCheckResponse
)
from app.api.dependencies import require_role


router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ============================================================================
# Protocol Management Endpoints
# ============================================================================

@router.post("/protocols", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
def create_protocol(
    protocol_data: ProtocolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN))
):
    """
    Create a new protocol (admin only).

    Creates a new protocol in draft status. Only platform admins can create protocols.

    Args:
        protocol_data: Protocol creation data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        ProtocolResponse: Created protocol data

    Raises:
        HTTPException: If validation fails or user lacks permissions
    """
    # Create new protocol
    protocol = Protocol(
        name=protocol_data.name,
        version=protocol_data.version,
        therapy_type=protocol_data.therapy_type,
        condition_treated=protocol_data.condition_treated,
        evidence_level=protocol_data.evidence_level,
        overview=protocol_data.overview,
        duration_weeks=protocol_data.duration_weeks,
        total_sessions=protocol_data.total_sessions,
        evidence_sources=protocol_data.evidence_sources,
        created_by=current_user.id,
        status="draft"
    )

    db.add(protocol)
    db.commit()
    db.refresh(protocol)

    return protocol


@router.put("/protocols/{protocol_id}", response_model=ProtocolResponse)
def update_protocol(
    protocol_id: int,
    protocol_data: ProtocolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN))
):
    """
    Update an existing protocol (admin only).

    Updates protocol fields. Only fields provided in the request will be updated.

    Args:
        protocol_id: ID of protocol to update
        protocol_data: Protocol update data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        ProtocolResponse: Updated protocol data

    Raises:
        HTTPException: If protocol not found or user lacks permissions
    """
    # Find protocol
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found"
        )

    # Update fields
    update_data = protocol_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(protocol, field, value)

    db.commit()
    db.refresh(protocol)

    return protocol


@router.delete("/protocols/{protocol_id}")
def delete_protocol(
    protocol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN))
):
    """
    Delete (archive) a protocol (admin only).

    Soft deletes a protocol by setting its status to "archived".
    This preserves historical data.

    Args:
        protocol_id: ID of protocol to archive
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        dict: Success message

    Raises:
        HTTPException: If protocol not found or user lacks permissions
    """
    # Find protocol
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found"
        )

    # Soft delete (archive)
    protocol.status = "archived"
    db.commit()

    return {"message": "Protocol archived successfully"}


# ============================================================================
# Protocol Step Endpoints
# ============================================================================

@router.post("/protocols/{protocol_id}/steps", response_model=ProtocolStepResponse, status_code=status.HTTP_201_CREATED)
def add_step_to_protocol(
    protocol_id: int,
    step_data: ProtocolStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN))
):
    """
    Add a step to a protocol (admin only).

    Creates a new step within a protocol. Steps define the workflow
    of the treatment protocol.

    Args:
        protocol_id: ID of protocol to add step to
        step_data: Step creation data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        ProtocolStepResponse: Created step data

    Raises:
        HTTPException: If protocol not found or user lacks permissions
    """
    # Verify protocol exists
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found"
        )

    # Create step
    step = ProtocolStep(
        protocol_id=protocol_id,
        sequence_order=step_data.sequence_order,
        step_type=step_data.step_type,
        title=step_data.title,
        description=step_data.description,
        duration_minutes=step_data.duration_minutes,
        required_roles=step_data.required_roles,
        clinical_scales=step_data.clinical_scales,
        evaluation_rules=step_data.evaluation_rules,
        branch_outcomes=step_data.branch_outcomes,
        vitals_monitoring=step_data.vitals_monitoring
    )

    db.add(step)
    db.commit()
    db.refresh(step)

    return step


@router.put("/protocols/{protocol_id}/steps/{step_id}", response_model=ProtocolStepResponse)
def update_protocol_step(
    protocol_id: int,
    step_id: int,
    step_data: ProtocolStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN))
):
    """
    Update a protocol step (admin only).

    Updates step fields. Only fields provided in the request will be updated.

    Args:
        protocol_id: ID of protocol
        step_id: ID of step to update
        step_data: Step update data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        ProtocolStepResponse: Updated step data

    Raises:
        HTTPException: If protocol or step not found or user lacks permissions
    """
    # Find step
    step = db.query(ProtocolStep).filter(
        ProtocolStep.id == step_id,
        ProtocolStep.protocol_id == protocol_id
    ).first()

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )

    # Update fields
    update_data = step_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(step, field, value)

    db.commit()
    db.refresh(step)

    return step


@router.delete("/protocols/{protocol_id}/steps/{step_id}")
def delete_protocol_step(
    protocol_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN))
):
    """
    Delete a protocol step (admin only).

    Permanently deletes a step from a protocol.

    Args:
        protocol_id: ID of protocol
        step_id: ID of step to delete
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        dict: Success message

    Raises:
        HTTPException: If protocol or step not found or user lacks permissions
    """
    # Find step
    step = db.query(ProtocolStep).filter(
        ProtocolStep.id == step_id,
        ProtocolStep.protocol_id == protocol_id
    ).first()

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )

    # Delete step
    db.delete(step)
    db.commit()

    return {"message": "Step deleted successfully"}


# ============================================================================
# Safety Check Endpoints
# ============================================================================

@router.post("/protocols/{protocol_id}/steps/{step_id}/safety-checks", response_model=SafetyCheckResponse, status_code=status.HTTP_201_CREATED)
def add_safety_check(
    protocol_id: int,
    step_id: int,
    safety_data: SafetyCheckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN))
):
    """
    Add a safety check to a protocol step (admin only).

    Creates a new safety check (contraindication or risk factor) for a step.
    Safety checks are evaluated during protocol execution.

    Args:
        protocol_id: ID of protocol
        step_id: ID of step to add safety check to
        safety_data: Safety check creation data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        SafetyCheckResponse: Created safety check data

    Raises:
        HTTPException: If protocol or step not found or user lacks permissions
    """
    # Verify step exists and belongs to protocol
    step = db.query(ProtocolStep).filter(
        ProtocolStep.id == step_id,
        ProtocolStep.protocol_id == protocol_id
    ).first()

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )

    # Create safety check
    safety_check = SafetyCheck(
        protocol_step_id=step_id,
        check_type=safety_data.check_type,
        condition=safety_data.condition,
        severity=safety_data.severity,
        override_allowed=safety_data.override_allowed,
        override_requirements=safety_data.override_requirements,
        evidence_source=safety_data.evidence_source
    )

    db.add(safety_check)
    db.commit()
    db.refresh(safety_check)

    return safety_check


# ============================================================================
# Protocol Publishing Endpoint
# ============================================================================

@router.post("/protocols/{protocol_id}/publish", response_model=ProtocolResponse)
def publish_protocol(
    protocol_id: int,
    publish_data: ProtocolPublish,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN))
):
    """
    Publish a protocol (admin only).

    Changes protocol status from "draft" to "active", making it available
    for use in treatment plans.

    Args:
        protocol_id: ID of protocol to publish
        publish_data: Empty publish request
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        ProtocolResponse: Published protocol data

    Raises:
        HTTPException: If protocol not found or user lacks permissions
    """
    # Find protocol
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found"
        )

    # Set status to active
    protocol.status = "active"
    db.commit()
    db.refresh(protocol)

    return protocol
