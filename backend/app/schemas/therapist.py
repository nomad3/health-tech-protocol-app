from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PatientBasicInfo(BaseModel):
    """Basic patient information for therapist views."""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TodaySession(BaseModel):
    """Session information for today's schedule."""
    id: int
    patient_id: int
    patient_email: str
    scheduled_at: datetime
    status: str
    location: str
    step_title: str

    class Config:
        from_attributes = True


class PendingTask(BaseModel):
    """Pending task for therapist."""
    task_type: str  # documentation, decision_point, review
    session_id: Optional[int] = None
    treatment_plan_id: Optional[int] = None
    description: str
    priority: str  # high, medium, low
    due_date: Optional[datetime] = None


class TherapistDashboardResponse(BaseModel):
    """Dashboard data for therapist."""
    today_sessions: List[TodaySession]
    pending_tasks: List[PendingTask]
    active_patients_count: int
    upcoming_sessions_count: int


class PatientTreatmentInfo(BaseModel):
    """Patient information with treatment details."""
    id: int
    email: str
    date_of_birth: Optional[str] = None
    treatment_plan_id: Optional[int] = None
    protocol_name: Optional[str] = None
    treatment_status: Optional[str] = None
    next_session: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """List of therapist's patients."""
    patients: List[PatientTreatmentInfo]
    total_count: int


class TreatmentPlanCreate(BaseModel):
    """Schema for creating a treatment plan."""
    patient_id: int = Field(..., description="Patient user ID")
    protocol_id: int = Field(..., description="Protocol ID to use")
    start_date: datetime = Field(..., description="Treatment start date")
    customizations: Optional[Dict[str, Any]] = Field(None, description="Protocol customizations")


class TreatmentPlanResponse(BaseModel):
    """Response schema for treatment plan."""
    id: int
    patient_id: int
    therapist_id: int
    clinic_id: Optional[int]
    protocol_id: int
    protocol_version: str
    status: str
    start_date: datetime
    estimated_completion: Optional[datetime]
    customizations: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionVitalsLog(BaseModel):
    """Schema for logging vitals during a session."""
    blood_pressure: Optional[str] = Field(None, description="Blood pressure reading (e.g., '120/80')")
    heart_rate: Optional[int] = Field(None, description="Heart rate in BPM")
    temperature: Optional[float] = Field(None, description="Body temperature in Fahrenheit")
    spo2: Optional[int] = Field(None, description="Blood oxygen saturation percentage")
    timestamp: datetime = Field(..., description="Timestamp of vitals reading")
    notes: Optional[str] = Field(None, description="Additional notes about vitals")


class SessionVitalsResponse(BaseModel):
    """Response after logging vitals."""
    message: str
    vitals_logged: int
    session_id: int


class ClinicalScale(BaseModel):
    """Clinical scale assessment."""
    scale_name: str = Field(..., description="Name of clinical scale (e.g., PHQ-9, GAD-7)")
    score: int = Field(..., description="Total score")
    subscores: Optional[Dict[str, Any]] = Field(None, description="Subscale scores if applicable")
    interpretation: Optional[str] = Field(None, description="Score interpretation")


class AdverseEvent(BaseModel):
    """Adverse event during session."""
    event_type: str = Field(..., description="Type of adverse event")
    severity: str = Field(..., description="Severity: mild, moderate, severe")
    description: str = Field(..., description="Description of the event")
    timestamp: datetime = Field(..., description="When the event occurred")
    action_taken: str = Field(..., description="Action taken in response")


class SessionDocumentationCreate(BaseModel):
    """Schema for creating/updating session documentation."""
    therapist_notes: Optional[str] = Field(None, description="Therapist's clinical notes")
    patient_subjective_notes: Optional[str] = Field(None, description="Patient's subjective experience")
    clinical_scales: Optional[Dict[str, Any]] = Field(None, description="Clinical scale assessments")
    adverse_events: Optional[List[Dict[str, Any]]] = Field(None, description="Adverse events during session")


class SessionDocumentationResponse(BaseModel):
    """Response after saving session documentation."""
    id: int
    treatment_session_id: int
    message: str

    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    """Detailed session information."""
    id: int
    treatment_plan_id: int
    protocol_step_id: int
    scheduled_at: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    status: str
    location: str
    therapist_id: int
    patient_id: int
    patient_email: str
    step_title: str
    step_description: Optional[str]
    vitals: Optional[List[Dict[str, Any]]]
    documentation: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class SessionCompleteResponse(BaseModel):
    """Response after completing a session."""
    id: int
    status: str
    actual_end: datetime
    message: str

    class Config:
        from_attributes = True


class DecisionPointEvaluation(BaseModel):
    """Schema for evaluating a decision point."""
    treatment_plan_id: int = Field(..., description="Treatment plan ID")
    evaluation_criteria: Dict[str, Any] = Field(..., description="Evaluation criteria and measurements")
    recommendation: str = Field(..., description="Treatment recommendation (continue, adjust, discontinue)")
    notes: Optional[str] = Field(None, description="Additional notes about the evaluation")


class DecisionPointResponse(BaseModel):
    """Response after evaluating a decision point."""
    decision_point_id: int
    treatment_plan_id: int
    recommendation: str
    evaluation_data: Dict[str, Any]
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True


class PatientDetailResponse(BaseModel):
    """Comprehensive patient details for therapist view."""
    id: int
    email: str
    full_name: str
    date_of_birth: Optional[datetime] = None
    medical_history: Optional[Dict[str, Any]] = None
    medications: Optional[List[str]] = None
    contraindications: Optional[List[str]] = None
    treatment_plans: List[TreatmentPlanResponse]
    session_history: List[SessionDetailResponse]

    class Config:
        from_attributes = True
