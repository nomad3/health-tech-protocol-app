from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.protocol import TherapyType
from app.models.treatment import TreatmentStatus


class ProviderSearchFilters(BaseModel):
    """Schema for searching therapists/clinics."""
    location: Optional[str] = Field(None, description="Location (city, state, or zip code)")
    therapy_type: Optional[TherapyType] = Field(None, description="Type of therapy")
    protocol: Optional[str] = Field(None, description="Protocol name")
    availability: Optional[str] = Field(None, description="Availability (e.g., 'next_week', 'next_month')")

    model_config = {"from_attributes": True}


class ClinicInfo(BaseModel):
    """Schema for clinic information."""
    id: int
    name: str
    type: str
    address: Optional[str] = None

    model_config = {"from_attributes": True}


class TherapistInfo(BaseModel):
    """Schema for therapist information."""
    id: int
    user_id: int
    email: str
    license_type: str
    license_number: str
    license_state: str
    specialties: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    protocols_certified: Optional[List[str]] = None

    model_config = {"from_attributes": True}


class ProviderResponse(BaseModel):
    """Schema for returning provider info (therapist + clinic)."""
    therapist: TherapistInfo
    clinic: Optional[ClinicInfo] = None

    model_config = {"from_attributes": True}


class PreScreeningRequest(BaseModel):
    """Schema for pre-screening quiz request."""
    protocol_id: int
    responses: dict = Field(..., description="Quiz responses (question_id -> answer)")

    model_config = {"from_attributes": True}


class PreScreeningResponse(BaseModel):
    """Schema for pre-screening quiz response with risk assessment."""
    risk_level: str = Field(..., description="Risk level: 'low', 'medium', 'high', 'excluded'")
    eligible: bool = Field(..., description="Whether patient is eligible for protocol")
    contraindications: List[str] = Field(default_factory=list, description="List of detected contraindications")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for next steps")

    model_config = {"from_attributes": True}


class ConsultationRequest(BaseModel):
    """Schema for requesting consultation with provider."""
    therapist_id: int
    protocol_id: int
    preferred_date: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class TreatmentPlanResponse(BaseModel):
    """Schema for patient's treatment plan response."""
    id: int
    protocol_id: int
    protocol_name: str
    protocol_version: str
    therapist_id: int
    therapist_name: str
    clinic_id: Optional[int] = None
    clinic_name: Optional[str] = None
    status: TreatmentStatus
    start_date: datetime
    estimated_completion: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TreatmentPlanDetailResponse(BaseModel):
    """Schema for detailed treatment plan response."""
    id: int
    protocol_id: int
    protocol_name: str
    protocol_version: str
    therapist_id: int
    therapist_name: str
    clinic_id: Optional[int] = None
    clinic_name: Optional[str] = None
    status: TreatmentStatus
    start_date: datetime
    estimated_completion: Optional[datetime] = None
    customizations: Optional[dict] = None
    sessions: List[dict] = Field(default_factory=list, description="List of treatment sessions")
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsentRequest(BaseModel):
    """Schema for digital consent signing."""
    treatment_plan_id: int
    consent_text: str = Field(..., description="The full consent text being agreed to")
    signature: str = Field(..., description="Digital signature (patient's full name)")
    agreed: bool = Field(..., description="Explicit agreement to terms")

    model_config = {"from_attributes": True}


class ConsentResponse(BaseModel):
    """Schema for consent response."""
    id: int
    treatment_plan_id: int
    signed_at: datetime
    signature: str
    consent_version: str

    model_config = {"from_attributes": True}
