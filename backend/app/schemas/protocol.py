from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from app.models.protocol import TherapyType, EvidenceLevel, StepType


# ============================================================================
# Admin Creation Schemas
# ============================================================================

class ProtocolCreate(BaseModel):
    """Schema for creating a new protocol (admin only)."""
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    therapy_type: TherapyType
    condition_treated: str = Field(..., min_length=1, max_length=255)
    evidence_level: EvidenceLevel
    overview: Optional[str] = None
    duration_weeks: Optional[int] = Field(None, gt=0)
    total_sessions: Optional[int] = Field(None, gt=0)
    evidence_sources: Optional[List[str]] = None


class ProtocolUpdate(BaseModel):
    """Schema for updating a protocol (admin only)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    therapy_type: Optional[TherapyType] = None
    condition_treated: Optional[str] = Field(None, min_length=1, max_length=255)
    evidence_level: Optional[EvidenceLevel] = None
    overview: Optional[str] = None
    duration_weeks: Optional[int] = Field(None, gt=0)
    total_sessions: Optional[int] = Field(None, gt=0)
    evidence_sources: Optional[List[str]] = None


class ProtocolStepCreate(BaseModel):
    """Schema for creating a protocol step (admin only)."""
    sequence_order: int = Field(..., gt=0)
    step_type: StepType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    required_roles: Optional[List[str]] = None
    clinical_scales: Optional[List[str]] = None
    evaluation_rules: Optional[Dict[str, Any]] = None
    branch_outcomes: Optional[Dict[str, Any]] = None
    vitals_monitoring: Optional[Dict[str, Any]] = None


class ProtocolStepUpdate(BaseModel):
    """Schema for updating a protocol step (admin only)."""
    sequence_order: Optional[int] = Field(None, gt=0)
    step_type: Optional[StepType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    required_roles: Optional[List[str]] = None
    clinical_scales: Optional[List[str]] = None
    evaluation_rules: Optional[Dict[str, Any]] = None
    branch_outcomes: Optional[Dict[str, Any]] = None
    vitals_monitoring: Optional[Dict[str, Any]] = None


class SafetyCheckCreate(BaseModel):
    """Schema for creating a safety check (admin only)."""
    check_type: str = Field(..., min_length=1, max_length=100)
    condition: Dict[str, Any] = Field(...)
    severity: str = Field(..., pattern="^(blocking|warning|info)$")
    override_allowed: str = Field(default="false", pattern="^(true|false)$")
    override_requirements: Optional[Dict[str, Any]] = None
    evidence_source: Optional[str] = Field(None, max_length=255)


class ProtocolPublish(BaseModel):
    """Schema for publishing a protocol (admin only)."""
    # Empty schema - just a POST to trigger publish action
    pass


# ============================================================================
# Response Schemas
# ============================================================================

class SafetyCheckResponse(BaseModel):
    """Schema for safety check response."""
    id: int
    protocol_step_id: int
    check_type: str
    condition: Dict[str, Any]
    severity: str
    override_allowed: str
    override_requirements: Optional[Dict[str, Any]] = None
    evidence_source: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProtocolStepResponse(BaseModel):
    """Schema for protocol step response."""
    id: int
    protocol_id: int
    sequence_order: int
    step_type: StepType
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    required_roles: Optional[List[str]] = None
    clinical_scales: Optional[List[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProtocolResponse(BaseModel):
    """Schema for protocol response (basic info)."""
    id: int
    name: str
    version: str
    status: str
    therapy_type: TherapyType
    condition_treated: str
    evidence_level: EvidenceLevel
    overview: Optional[str] = None
    duration_weeks: Optional[int] = None
    total_sessions: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProtocolDetailResponse(ProtocolResponse):
    """Schema for detailed protocol response with additional metadata."""
    evidence_sources: Optional[List[str]] = None
    step_count: int = Field(default=0, description="Number of steps in the protocol")

    model_config = {"from_attributes": True}


class ProtocolListResponse(BaseModel):
    """Schema for paginated protocol list response."""
    items: List[ProtocolResponse]
    total: int
    page: int
    size: int

    model_config = {"from_attributes": True}


class ProtocolSearchResponse(BaseModel):
    """Schema for protocol search results."""
    items: List[ProtocolResponse]
    total: int

    model_config = {"from_attributes": True}
