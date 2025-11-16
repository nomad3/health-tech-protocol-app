from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, String
from app.database import get_db
from app.models.protocol import Protocol, ProtocolStep, TherapyType, EvidenceLevel
from app.schemas.protocol import (
    ProtocolResponse,
    ProtocolDetailResponse,
    ProtocolListResponse,
    ProtocolStepResponse,
    ProtocolSearchResponse,
)

router = APIRouter(prefix="/api/v1/protocols", tags=["protocols"])


@router.get("", response_model=ProtocolListResponse)
def list_protocols(
    therapy_type: Optional[TherapyType] = Query(None, description="Filter by therapy type"),
    condition: Optional[str] = Query(None, description="Filter by condition treated"),
    evidence_level: Optional[EvidenceLevel] = Query(None, description="Filter by evidence level"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    List all active protocols with optional filtering.
    Public endpoint - no authentication required.
    """
    # Start with query for active protocols only
    query = db.query(Protocol).filter(Protocol.status == "active")

    # Apply filters
    if therapy_type:
        query = query.filter(Protocol.therapy_type == therapy_type)
    if condition:
        query = query.filter(Protocol.condition_treated == condition)
    if evidence_level:
        query = query.filter(Protocol.evidence_level == evidence_level)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * size
    protocols = query.offset(offset).limit(size).all()

    return ProtocolListResponse(
        items=[ProtocolResponse.model_validate(p) for p in protocols],
        total=total,
        page=page,
        size=size,
    )


@router.get("/search", response_model=ProtocolSearchResponse)
def search_protocols(
    q: str = Query("", description="Search query"),
    db: Session = Depends(get_db),
):
    """
    Search protocols by name, overview, condition, or therapy type.
    Public endpoint - no authentication required.
    """
    # Start with active protocols only
    query = db.query(Protocol).filter(Protocol.status == "active")

    # Apply search filter if query provided
    if q:
        search_term = f"%{q.lower()}%"
        # Cast enum to text for LIKE comparison
        query = query.filter(
            or_(
                func.lower(Protocol.name).like(search_term),
                func.lower(Protocol.overview).like(search_term),
                func.lower(Protocol.condition_treated).like(search_term),
                func.lower(func.cast(Protocol.therapy_type, String)).like(search_term),
            )
        )

    protocols = query.all()

    return ProtocolSearchResponse(
        items=[ProtocolResponse.model_validate(p) for p in protocols],
        total=len(protocols),
    )


@router.get("/{protocol_id}", response_model=ProtocolDetailResponse)
def get_protocol_detail(
    protocol_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific protocol.
    Public endpoint - no authentication required.
    """
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()

    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")

    # Count steps
    step_count = db.query(func.count(ProtocolStep.id)).filter(
        ProtocolStep.protocol_id == protocol_id
    ).scalar() or 0

    # Convert to response model and add step count
    protocol_dict = {
        "id": protocol.id,
        "name": protocol.name,
        "version": protocol.version,
        "status": protocol.status,
        "therapy_type": protocol.therapy_type,
        "condition_treated": protocol.condition_treated,
        "evidence_level": protocol.evidence_level,
        "overview": protocol.overview,
        "duration_weeks": protocol.duration_weeks,
        "total_sessions": protocol.total_sessions,
        "evidence_sources": protocol.evidence_sources,
        "created_at": protocol.created_at,
        "updated_at": protocol.updated_at,
        "step_count": step_count,
    }

    return ProtocolDetailResponse(**protocol_dict)


@router.get("/{protocol_id}/steps", response_model=List[ProtocolStepResponse])
def get_protocol_steps(
    protocol_id: int,
    db: Session = Depends(get_db),
):
    """
    Get all steps for a specific protocol, ordered by sequence.
    Public endpoint - no authentication required.
    """
    # Check if protocol exists
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")

    # Get steps ordered by sequence
    steps = (
        db.query(ProtocolStep)
        .filter(ProtocolStep.protocol_id == protocol_id)
        .order_by(ProtocolStep.sequence_order)
        .all()
    )

    return [ProtocolStepResponse.model_validate(step) for step in steps]
