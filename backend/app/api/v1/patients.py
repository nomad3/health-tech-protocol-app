from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.protocol import Protocol, TherapyType
from app.models.profiles import TherapistProfile, Clinic, PatientProfile
from app.models.treatment import TreatmentPlan, TreatmentStatus
from app.schemas.patient import (
    ProviderSearchFilters,
    ProviderResponse,
    TherapistInfo,
    ClinicInfo,
    PreScreeningRequest,
    PreScreeningResponse,
    ConsultationRequest,
    TreatmentPlanResponse,
    TreatmentPlanDetailResponse,
    ConsentRequest,
    ConsentResponse,
)
from app.api.dependencies import get_current_user


router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


@router.get("/providers/search", response_model=List[ProviderResponse])
def search_providers(
    location: Optional[str] = Query(None, description="Location (city, state, or zip code)"),
    therapy_type: Optional[TherapyType] = Query(None, description="Type of therapy"),
    protocol: Optional[str] = Query(None, description="Protocol name"),
    availability: Optional[str] = Query(None, description="Availability"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search for therapists and clinics.

    Requires authentication (any role).

    Args:
        location: Location filter (optional)
        therapy_type: Therapy type filter (optional)
        protocol: Protocol name filter (optional)
        availability: Availability filter (optional)
        current_user: Current authenticated user
        db: Database session

    Returns:
        List[ProviderResponse]: List of providers matching filters
    """
    # Start with all therapist profiles
    query = db.query(TherapistProfile).join(User, TherapistProfile.user_id == User.id)

    # Apply filters
    if location:
        # Filter by clinic address or therapist license state
        query = query.outerjoin(Clinic, TherapistProfile.clinic_id == Clinic.id)
        query = query.filter(
            (TherapistProfile.license_state.ilike(f"%{location}%")) |
            (Clinic.address.ilike(f"%{location}%"))
        )

    # Note: Filtering by therapy_type and protocol would require more complex JSON queries
    # For MVP, we're doing simple filtering. In production, this would be more sophisticated
    # with proper JSON indexing and queries

    therapist_profiles = query.all()

    # Build response with therapist and clinic info
    providers = []
    for tp in therapist_profiles:
        # Get therapist user info
        therapist_user = db.query(User).filter(User.id == tp.user_id).first()

        therapist_info = TherapistInfo(
            id=tp.id,
            user_id=tp.user_id,
            email=therapist_user.email,
            license_type=tp.license_type,
            license_number=tp.license_number,
            license_state=tp.license_state,
            specialties=tp.specialties,
            certifications=tp.certifications,
            protocols_certified=tp.protocols_certified,
        )

        clinic_info = None
        if tp.clinic_id:
            clinic = db.query(Clinic).filter(Clinic.id == tp.clinic_id).first()
            if clinic:
                clinic_info = ClinicInfo(
                    id=clinic.id,
                    name=clinic.name,
                    type=clinic.type,
                    address=clinic.address,
                )

        providers.append(
            ProviderResponse(therapist=therapist_info, clinic=clinic_info)
        )

    return providers


@router.post("/protocols/{protocol_id}/pre-screen", response_model=PreScreeningResponse)
def pre_screen_protocol(
    protocol_id: int,
    request: PreScreeningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit pre-screening quiz for a protocol.

    Requires authentication (any role).

    Args:
        protocol_id: Protocol ID to screen for
        request: Pre-screening quiz responses
        current_user: Current authenticated user
        db: Database session

    Returns:
        PreScreeningResponse: Risk assessment and eligibility result

    Raises:
        HTTPException: If protocol not found
    """
    # Verify protocol exists
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found"
        )

    # Simple risk assessment algorithm
    # In production, this would be more sophisticated and protocol-specific
    responses = request.responses
    contraindications = []
    risk_level = "low"
    eligible = True

    # Check for common contraindications
    if responses.get("heart_condition"):
        contraindications.append("Pre-existing heart condition")
        risk_level = "high"

    if responses.get("psychosis_history"):
        contraindications.append("History of psychosis")
        risk_level = "excluded"
        eligible = False

    if responses.get("bipolar_disorder"):
        contraindications.append("Bipolar disorder")
        risk_level = "high"

    # Age check
    age = responses.get("age", 0)
    if age < 18:
        contraindications.append("Under 18 years old")
        risk_level = "excluded"
        eligible = False
    elif age > 65:
        risk_level = "medium"

    # Medications check
    medications = responses.get("medications", [])
    if "MAOI" in medications or "maoi" in str(medications).lower():
        contraindications.append("Taking MAOI medications")
        risk_level = "high"

    # Generate recommendations
    recommendations = []
    if eligible:
        if risk_level == "low":
            recommendations.append("You appear to be a good candidate for this protocol")
            recommendations.append("Schedule a consultation with a therapist to proceed")
        elif risk_level == "medium":
            recommendations.append("You may be eligible with additional screening")
            recommendations.append("Consultation with medical director recommended")
        elif risk_level == "high":
            recommendations.append("Additional medical evaluation required")
            recommendations.append("Consultation with medical director required")
    else:
        recommendations.append("You may not be eligible for this protocol at this time")
        recommendations.append("Please consult with a healthcare provider")

    return PreScreeningResponse(
        risk_level=risk_level,
        eligible=eligible,
        contraindications=contraindications,
        recommendations=recommendations,
    )


@router.post("/consultation-request", status_code=status.HTTP_201_CREATED)
def request_consultation(
    request: ConsultationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Request a consultation with a therapist.

    Requires authentication (any role).

    Args:
        request: Consultation request details
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Confirmation message with consultation ID

    Raises:
        HTTPException: If therapist or protocol not found
    """
    # Verify therapist exists
    therapist = db.query(User).filter(User.id == request.therapist_id).first()
    if not therapist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapist not found"
        )

    # Verify protocol exists
    protocol = db.query(Protocol).filter(Protocol.id == request.protocol_id).first()
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found"
        )

    # In a real implementation, this would create a ConsultationRequest record
    # For now, we'll return a success response
    # Future: Store in database and notify therapist

    return {
        "message": "Consultation request submitted successfully",
        "consultation_id": 1,  # Placeholder
        "therapist_id": request.therapist_id,
        "protocol_id": request.protocol_id,
        "status": "pending"
    }


@router.get("/treatment-plans", response_model=List[TreatmentPlanResponse])
def get_my_treatment_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all treatment plans for the current user.

    Requires authentication (any role, but filters to current user).

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List[TreatmentPlanResponse]: List of treatment plans
    """
    # Get all treatment plans for current user
    plans = (
        db.query(TreatmentPlan)
        .filter(TreatmentPlan.patient_id == current_user.id)
        .all()
    )

    # Build response
    result = []
    for plan in plans:
        # Get protocol
        protocol = db.query(Protocol).filter(Protocol.id == plan.protocol_id).first()

        # Get therapist
        therapist = db.query(User).filter(User.id == plan.therapist_id).first()

        # Get clinic if exists
        clinic_name = None
        if plan.clinic_id:
            clinic = db.query(Clinic).filter(Clinic.id == plan.clinic_id).first()
            if clinic:
                clinic_name = clinic.name

        result.append(
            TreatmentPlanResponse(
                id=plan.id,
                protocol_id=plan.protocol_id,
                protocol_name=protocol.name if protocol else "Unknown",
                protocol_version=plan.protocol_version,
                therapist_id=plan.therapist_id,
                therapist_name=therapist.email if therapist else "Unknown",
                clinic_id=plan.clinic_id,
                clinic_name=clinic_name,
                status=plan.status,
                start_date=plan.start_date,
                estimated_completion=plan.estimated_completion,
                created_at=plan.created_at,
            )
        )

    return result


@router.get("/treatment-plans/{plan_id}", response_model=TreatmentPlanDetailResponse)
def get_treatment_plan_details(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific treatment plan.

    Requires authentication and ownership of the treatment plan.

    Args:
        plan_id: Treatment plan ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        TreatmentPlanDetailResponse: Detailed treatment plan information

    Raises:
        HTTPException: If plan not found or user doesn't have access
    """
    # Get treatment plan
    plan = db.query(TreatmentPlan).filter(TreatmentPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treatment plan not found"
        )

    # Verify ownership (patient can only see their own plans)
    if plan.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this treatment plan"
        )

    # Get protocol
    protocol = db.query(Protocol).filter(Protocol.id == plan.protocol_id).first()

    # Get therapist
    therapist = db.query(User).filter(User.id == plan.therapist_id).first()

    # Get clinic if exists
    clinic_name = None
    if plan.clinic_id:
        clinic = db.query(Clinic).filter(Clinic.id == plan.clinic_id).first()
        if clinic:
            clinic_name = clinic.name

    # Get sessions
    sessions = []
    for session in plan.sessions:
        sessions.append({
            "id": session.id,
            "scheduled_at": session.scheduled_at.isoformat(),
            "status": session.status.value,
            "location": session.location,
        })

    return TreatmentPlanDetailResponse(
        id=plan.id,
        protocol_id=plan.protocol_id,
        protocol_name=protocol.name if protocol else "Unknown",
        protocol_version=plan.protocol_version,
        therapist_id=plan.therapist_id,
        therapist_name=therapist.email if therapist else "Unknown",
        clinic_id=plan.clinic_id,
        clinic_name=clinic_name,
        status=plan.status,
        start_date=plan.start_date,
        estimated_completion=plan.estimated_completion,
        customizations=plan.customizations,
        sessions=sessions,
        created_at=plan.created_at,
    )


@router.post("/consent/{plan_id}", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
def sign_consent(
    plan_id: int,
    request: ConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sign informed consent for a treatment plan.

    Requires authentication and ownership of the treatment plan.

    Args:
        plan_id: Treatment plan ID
        request: Consent signing request
        current_user: Current authenticated user
        db: Database session

    Returns:
        ConsentResponse: Signed consent confirmation

    Raises:
        HTTPException: If plan not found, user doesn't have access, or consent not agreed
    """
    # Verify treatment plan exists
    plan = db.query(TreatmentPlan).filter(TreatmentPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treatment plan not found"
        )

    # Verify ownership
    if plan.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this treatment plan"
        )

    # Verify consent is agreed
    if not request.agreed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must agree to the consent terms"
        )

    # In a real implementation, this would create a Consent record in the database
    # For now, we'll return a success response
    # Future: Store consent in database with timestamp and version

    return ConsentResponse(
        id=1,  # Placeholder
        treatment_plan_id=plan_id,
        signed_at=datetime.utcnow(),
        signature=request.signature,
        consent_version="1.0",
    )
