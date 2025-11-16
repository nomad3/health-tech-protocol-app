"""Pydantic schemas for AI integration endpoints.

This module defines request/response schemas for:
- Protocol extraction from research text
- Patient education content generation
- Clinical decision support
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Protocol Extraction Schemas
# ============================================================================

class ProtocolExtractionRequest(BaseModel):
    """Request schema for extracting protocol from research text."""

    research_text: str = Field(
        ...,
        min_length=100,
        max_length=50000,
        description="Research paper or clinical guideline text to extract protocol from"
    )
    therapy_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of therapy (e.g., 'psilocybin', 'mdma', 'ketamine')"
    )
    condition: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Condition being treated (e.g., 'depression', 'ptsd')"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "research_text": "Clinical trial protocol for psilocybin-assisted therapy...",
            "therapy_type": "psilocybin",
            "condition": "treatment_resistant_depression"
        }
    }}


class ExtractedProtocol(BaseModel):
    """Extracted protocol structure."""

    name: str
    version: str
    therapy_type: str
    condition_treated: str
    evidence_level: str
    overview: Optional[str] = None
    duration_weeks: Optional[int] = None
    total_sessions: Optional[int] = None
    evidence_sources: Optional[List[str]] = None


class ExtractedProtocolStep(BaseModel):
    """Extracted protocol step structure."""

    sequence_order: int
    step_type: str
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    required_roles: Optional[List[str]] = None
    clinical_scales: Optional[List[str]] = None
    vitals_monitoring: Optional[Dict[str, bool]] = None


class ExtractedSafetyCheck(BaseModel):
    """Extracted safety check structure."""

    step_sequence: int
    check_type: str
    condition: Dict[str, Any]
    severity: str
    override_allowed: str
    evidence_source: Optional[str] = None


class ProtocolExtractionResponse(BaseModel):
    """Response schema for protocol extraction."""

    extracted_protocol: ExtractedProtocol
    steps: List[ExtractedProtocolStep]
    safety_checks: List[ExtractedSafetyCheck]
    extraction_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="AI confidence score for extraction quality"
    )
    warnings: Optional[List[str]] = Field(
        default=None,
        description="Any warnings or concerns about the extraction"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "extracted_protocol": {
                "name": "Psilocybin for Treatment-Resistant Depression",
                "version": "1.0",
                "therapy_type": "psilocybin",
                "condition_treated": "treatment_resistant_depression",
                "evidence_level": "phase_3_trial",
                "overview": "Multi-session protocol with preparation, dosing, and integration",
                "duration_weeks": 12,
                "total_sessions": 8,
                "evidence_sources": ["Carhart-Harris et al. 2021", "Davis et al. 2020"]
            },
            "steps": [
                {
                    "sequence_order": 1,
                    "step_type": "screening",
                    "title": "Initial Psychiatric Evaluation",
                    "description": "Comprehensive psychiatric assessment",
                    "duration_minutes": 90,
                    "required_roles": ["medical_director"],
                    "clinical_scales": ["MADRS", "BDI-II"]
                }
            ],
            "safety_checks": [],
            "extraction_confidence": 0.92,
            "warnings": ["Some dosage details were not specified in source text"]
        }
    }}


# ============================================================================
# Patient Education Schemas
# ============================================================================

class PatientContext(BaseModel):
    """Patient context for personalized education."""

    anxiety_level: str = Field(
        default="moderate",
        pattern="^(low|moderate|high)$",
        description="Patient's baseline anxiety level"
    )
    age_range: str = Field(
        default="adult",
        pattern="^(young_adult|adult|senior)$",
        description="Patient's age range"
    )
    education_level: str = Field(
        default="general",
        pattern="^(general|technical|medical)$",
        description="Patient's education level for content adaptation"
    )


class PatientEducationRequest(BaseModel):
    """Request schema for generating patient education content."""

    protocol_id: int = Field(
        ...,
        gt=0,
        description="ID of the protocol to generate education content for"
    )
    protocol_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the protocol"
    )
    condition: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Condition being treated"
    )
    patient_context: PatientContext = Field(
        default_factory=PatientContext,
        description="Patient-specific context for personalization"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "protocol_id": 1,
            "protocol_name": "Psilocybin for Depression",
            "condition": "treatment_resistant_depression",
            "patient_context": {
                "anxiety_level": "high",
                "age_range": "adult",
                "education_level": "general"
            }
        }
    }}


class PatientEducationResponse(BaseModel):
    """Response schema for patient education content."""

    education_text: str = Field(
        ...,
        description="Generated patient education content in Markdown format"
    )
    word_count: int = Field(
        ...,
        description="Word count of generated content"
    )
    reading_time_minutes: int = Field(
        ...,
        description="Estimated reading time in minutes"
    )
    generated_at: str = Field(
        ...,
        description="Timestamp of generation (ISO format)"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "education_text": "## Your Treatment Journey\n\nWe're glad you're here...",
            "word_count": 1250,
            "reading_time_minutes": 6,
            "generated_at": "2025-11-16T10:30:00Z"
        }
    }}


# ============================================================================
# Clinical Decision Support Schemas
# ============================================================================

class SessionData(BaseModel):
    """Current session data for decision support."""

    session_id: int
    step_sequence: int
    vitals: Dict[str, Any] = Field(
        default_factory=dict,
        description="Current vital signs (heart_rate, blood_pressure, etc.)"
    )
    adverse_events: List[str] = Field(
        default_factory=list,
        description="Any adverse events reported"
    )
    clinical_scales: Dict[str, float] = Field(
        default_factory=dict,
        description="Clinical scale scores (MADRS, BDI-II, etc.)"
    )
    subjective_experience: Optional[str] = Field(
        default=None,
        description="Patient's reported subjective experience"
    )


class ProtocolContext(BaseModel):
    """Protocol context for decision support."""

    protocol_name: str
    current_step_title: str
    step_type: str
    evaluation_rules: Optional[Dict[str, Any]] = None
    safety_thresholds: Optional[Dict[str, Any]] = None


class PatientHistory(BaseModel):
    """Patient history for decision support."""

    baseline_measures: Dict[str, float] = Field(
        default_factory=dict,
        description="Baseline clinical measures"
    )
    previous_sessions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Data from previous sessions"
    )
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Known risk factors"
    )
    medications: List[str] = Field(
        default_factory=list,
        description="Current medications"
    )


class ClinicalDecisionRequest(BaseModel):
    """Request schema for clinical decision support."""

    session_data: SessionData
    protocol_context: ProtocolContext
    patient_history: PatientHistory

    model_config = {"json_schema_extra": {
        "example": {
            "session_data": {
                "session_id": 5,
                "step_sequence": 3,
                "vitals": {
                    "heart_rate": 78,
                    "blood_pressure_systolic": 125,
                    "blood_pressure_diastolic": 82,
                    "temperature": 98.6
                },
                "adverse_events": [],
                "clinical_scales": {
                    "MADRS": 15,
                    "BDI-II": 18
                }
            },
            "protocol_context": {
                "protocol_name": "Psilocybin for Depression",
                "current_step_title": "Integration Session 1",
                "step_type": "integration",
                "evaluation_rules": {
                    "continue_if_madrs_below": 20
                }
            },
            "patient_history": {
                "baseline_measures": {
                    "MADRS": 32,
                    "BDI-II": 35
                },
                "previous_sessions": [],
                "risk_factors": [],
                "medications": []
            }
        }
    }}


class RiskFactor(BaseModel):
    """Identified risk factor."""

    factor: str = Field(..., description="Description of the risk factor")
    severity: str = Field(..., pattern="^(info|warning|urgent)$")
    recommendation: str = Field(..., description="Recommended action")


class ClinicalRecommendation(BaseModel):
    """Clinical recommendation."""

    category: str = Field(
        ...,
        pattern="^(safety|dosing|monitoring|followup|referral)$",
        description="Category of recommendation"
    )
    priority: str = Field(
        ...,
        pattern="^(high|medium|low)$",
        description="Priority level"
    )
    action: str = Field(..., description="Specific recommended action")
    rationale: str = Field(..., description="Evidence-based reasoning")
    evidence_basis: str = Field(..., description="Reference to protocol or research")


class DecisionPointEvaluation(BaseModel):
    """Evaluation of protocol decision point."""

    meets_continuation_criteria: bool
    reasons: List[str] = Field(
        default_factory=list,
        description="Reasons for the decision"
    )
    suggested_next_step: Optional[str] = None


class ClinicalDecisionResponse(BaseModel):
    """Response schema for clinical decision support."""

    risk_level: str = Field(
        ...,
        pattern="^(low|moderate|high|critical)$",
        description="Overall risk assessment"
    )
    risk_factors: List[RiskFactor] = Field(
        default_factory=list,
        description="Identified risk factors"
    )
    recommendations: List[ClinicalRecommendation] = Field(
        default_factory=list,
        description="Clinical recommendations"
    )
    decision_point_evaluation: Optional[DecisionPointEvaluation] = None
    clinical_notes: str = Field(
        ...,
        description="Summary for clinician's review"
    )
    requires_immediate_attention: bool = Field(
        default=False,
        description="Whether immediate intervention is needed"
    )
    suggested_interventions: List[str] = Field(
        default_factory=list,
        description="Specific interventions if needed"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="AI confidence in the assessment"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "risk_level": "low",
            "risk_factors": [],
            "recommendations": [
                {
                    "category": "monitoring",
                    "priority": "medium",
                    "action": "Continue standard vital signs monitoring",
                    "rationale": "Patient showing good clinical progress with MADRS improvement from 32 to 15",
                    "evidence_basis": "Protocol guidelines section 4.2"
                }
            ],
            "decision_point_evaluation": {
                "meets_continuation_criteria": True,
                "reasons": [
                    "MADRS score of 15 is below threshold of 20",
                    "No adverse events reported",
                    "Vitals within normal limits"
                ],
                "suggested_next_step": "Proceed to Integration Session 2"
            },
            "clinical_notes": "Patient demonstrates significant clinical improvement with excellent protocol compliance. Continue current treatment plan.",
            "requires_immediate_attention": False,
            "suggested_interventions": [],
            "confidence_score": 0.94
        }
    }}
