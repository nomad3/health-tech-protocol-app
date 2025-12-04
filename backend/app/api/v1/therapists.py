from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models.user import User, UserRole
from app.models.profiles import TherapistProfile, PatientProfile
from app.models.treatment import TreatmentPlan, TreatmentSession, SessionDocumentation, SessionStatus, TreatmentStatus
from app.models.protocol import ProtocolStep
from app.schemas.therapist import (
    TherapistDashboardResponse,
    TodaySession,
    PendingTask,
    PatientListResponse,
    PatientTreatmentInfo,
    TreatmentPlanCreate,
    TreatmentPlanResponse,
    SessionVitalsLog,
    SessionVitalsResponse,
    SessionDocumentationCreate,
    SessionDocumentationResponse,
    SessionDetailResponse,
    SessionCompleteResponse,
    DecisionPointEvaluation,
    DecisionPointResponse
)
from app.api.dependencies import get_current_user, require_role


router = APIRouter(prefix="/api/v1/therapist", tags=["therapist"])


def verify_therapist_owns_patient(therapist_id: int, patient_id: int, db: Session) -> bool:
    """
    Verify that the therapist has an active treatment plan with this patient.

    Args:
        therapist_id: Therapist user ID
        patient_id: Patient user ID
        db: Database session

    Returns:
        bool: True if therapist has active treatment plan with patient
    """
    treatment_plan = db.query(TreatmentPlan).filter(
        and_(
            TreatmentPlan.therapist_id == therapist_id,
            TreatmentPlan.patient_id == patient_id,
            TreatmentPlan.status.in_([TreatmentStatus.ACTIVE, TreatmentStatus.SCREENING])
        )
    ).first()
    return treatment_plan is not None


def verify_therapist_owns_session(therapist_id: int, session_id: int, db: Session) -> TreatmentSession:
    """
    Verify that the session belongs to this therapist and return it.

    Args:
        therapist_id: Therapist user ID
        session_id: Session ID
        db: Database session

    Returns:
        TreatmentSession: The session if owned by therapist

    Raises:
        HTTPException: If session not found or not owned by therapist
    """
    session = db.query(TreatmentSession).filter(
        TreatmentSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.therapist_id != therapist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this session"
        )

    return session


@router.get("/dashboard", response_model=TherapistDashboardResponse)
def get_therapist_dashboard(
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Get therapist dashboard with today's sessions and pending tasks.

    Args:
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        TherapistDashboardResponse: Dashboard data
    """
    # Get today's date range
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    # Get today's sessions
    today_sessions_query = db.query(TreatmentSession).join(
        TreatmentPlan, TreatmentSession.treatment_plan_id == TreatmentPlan.id
    ).join(
        ProtocolStep, TreatmentSession.protocol_step_id == ProtocolStep.id
    ).join(
        User, TreatmentPlan.patient_id == User.id
    ).filter(
        and_(
            TreatmentSession.therapist_id == current_user.id,
            TreatmentSession.scheduled_at >= today_start,
            TreatmentSession.scheduled_at <= today_end
        )
    ).all()

    today_sessions = []
    for session in today_sessions_query:
        treatment_plan = db.query(TreatmentPlan).filter(
            TreatmentPlan.id == session.treatment_plan_id
        ).first()
        patient = db.query(User).filter(User.id == treatment_plan.patient_id).first()
        step = db.query(ProtocolStep).filter(ProtocolStep.id == session.protocol_step_id).first()

        today_sessions.append(TodaySession(
            id=session.id,
            patient_id=treatment_plan.patient_id,
            patient_email=patient.email,
            scheduled_at=session.scheduled_at,
            status=session.status.value,
            location=session.location,
            step_title=step.title
        ))

    # Get pending tasks (sessions needing documentation)
    pending_tasks = []

    # Find completed sessions without documentation
    completed_sessions = db.query(TreatmentSession).outerjoin(
        SessionDocumentation
    ).filter(
        and_(
            TreatmentSession.therapist_id == current_user.id,
            TreatmentSession.status == SessionStatus.COMPLETED,
            SessionDocumentation.id.is_(None)
        )
    ).limit(10).all()

    for session in completed_sessions:
        pending_tasks.append(PendingTask(
            task_type="documentation",
            session_id=session.id,
            description=f"Complete documentation for session {session.id}",
            priority="high",
            due_date=None
        ))

    # Count active patients
    active_patients = db.query(TreatmentPlan).filter(
        and_(
            TreatmentPlan.therapist_id == current_user.id,
            TreatmentPlan.status.in_([TreatmentStatus.ACTIVE, TreatmentStatus.SCREENING])
        )
    ).count()

    # Count upcoming sessions (next 7 days)
    week_end = datetime.utcnow() + timedelta(days=7)
    upcoming_sessions = db.query(TreatmentSession).filter(
        and_(
            TreatmentSession.therapist_id == current_user.id,
            TreatmentSession.scheduled_at > datetime.utcnow(),
            TreatmentSession.scheduled_at <= week_end,
            TreatmentSession.status == SessionStatus.SCHEDULED
        )
    ).count()

    return TherapistDashboardResponse(
        today_sessions=today_sessions,
        pending_tasks=pending_tasks,
        active_patients_count=active_patients,
        upcoming_sessions_count=upcoming_sessions
    )


@router.get("/sessions/today", response_model=List[TodaySession])
def get_today_sessions(
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """Get all sessions scheduled for today."""
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    sessions = db.query(TreatmentSession).filter(
        and_(
            TreatmentSession.therapist_id == current_user.id,
            TreatmentSession.scheduled_at >= today_start,
            TreatmentSession.scheduled_at <= today_end
        )
    ).all()

    result = []
    for session in sessions:
        treatment_plan = db.query(TreatmentPlan).filter(TreatmentPlan.id == session.treatment_plan_id).first()
        patient = db.query(User).filter(User.id == treatment_plan.patient_id).first()
        step = db.query(ProtocolStep).filter(ProtocolStep.id == session.protocol_step_id).first()

        result.append(TodaySession(
            id=session.id,
            patient_id=treatment_plan.patient_id,
            patient_email=patient.email,
            scheduled_at=session.scheduled_at,
            status=session.status.value,
            location=session.location,
            step_title=step.title if step else "Unknown Step"
        ))
    return result


@router.get("/sessions/upcoming", response_model=List[TodaySession])
def get_upcoming_sessions(
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """Get upcoming sessions for the next 7 days."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(days=7)

    sessions = db.query(TreatmentSession).filter(
        and_(
            TreatmentSession.therapist_id == current_user.id,
            TreatmentSession.scheduled_at > start_time,
            TreatmentSession.scheduled_at <= end_time,
            TreatmentSession.status == SessionStatus.SCHEDULED
        )
    ).order_by(TreatmentSession.scheduled_at).all()

    result = []
    for session in sessions:
        treatment_plan = db.query(TreatmentPlan).filter(TreatmentPlan.id == session.treatment_plan_id).first()
        patient = db.query(User).filter(User.id == treatment_plan.patient_id).first()
        step = db.query(ProtocolStep).filter(ProtocolStep.id == session.protocol_step_id).first()

        result.append(TodaySession(
            id=session.id,
            patient_id=treatment_plan.patient_id,
            patient_email=patient.email,
            scheduled_at=session.scheduled_at,
            status=session.status.value,
            location=session.location,
            step_title=step.title if step else "Unknown Step"
        ))
    return result


@router.get("/patients", response_model=List[PatientTreatmentInfo])
def get_therapist_patients(
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Get list of all patients assigned to this therapist.

    Args:
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        List[PatientTreatmentInfo]: List of patients with treatment info
    """
    # Get all treatment plans for this therapist
    treatment_plans = db.query(TreatmentPlan).filter(
        TreatmentPlan.therapist_id == current_user.id
    ).all()

    patients_info = []
    seen_patients = set()

    for plan in treatment_plans:
        if plan.patient_id in seen_patients:
            continue
        seen_patients.add(plan.patient_id)

        patient = db.query(User).filter(User.id == plan.patient_id).first()
        patient_profile = db.query(PatientProfile).filter(
            PatientProfile.user_id == plan.patient_id
        ).first()

        # Get protocol name
        from app.models.protocol import Protocol
        protocol = db.query(Protocol).filter(Protocol.id == plan.protocol_id).first()

        # Get next scheduled session
        next_session = db.query(TreatmentSession).filter(
            and_(
                TreatmentSession.treatment_plan_id == plan.id,
                TreatmentSession.scheduled_at > datetime.utcnow(),
                TreatmentSession.status == SessionStatus.SCHEDULED
            )
        ).order_by(TreatmentSession.scheduled_at).first()

        patients_info.append(PatientTreatmentInfo(
            id=patient.id,
            email=patient.email,
            date_of_birth=str(patient_profile.date_of_birth) if patient_profile else None,
            treatment_plan_id=plan.id,
            protocol_name=protocol.name if protocol else None,
            treatment_status=plan.status.value,
            next_session=next_session.scheduled_at if next_session else None
        ))

    return patients_info


@router.get("/patients/{patient_id}", response_model=PatientDetailResponse)
def get_patient_details(
    patient_id: int,
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive details for a specific patient.

    Args:
        patient_id: Patient user ID
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        PatientDetailResponse: Detailed patient information
    """
    # Verify therapist has treated or is treating this patient
    has_relationship = db.query(TreatmentPlan).filter(
        and_(
            TreatmentPlan.therapist_id == current_user.id,
            TreatmentPlan.patient_id == patient_id
        )
    ).first()

    if not has_relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this patient's details"
        )

    # Get patient user info
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Get patient profile
    patient_profile = db.query(PatientProfile).filter(
        PatientProfile.user_id == patient_id
    ).first()

    # Get all treatment plans
    treatment_plans = db.query(TreatmentPlan).filter(
        and_(
            TreatmentPlan.patient_id == patient_id,
            TreatmentPlan.therapist_id == current_user.id
        )
    ).all()

    # Get session history
    # We want all sessions for these treatment plans
    plan_ids = [plan.id for plan in treatment_plans]
    sessions = db.query(TreatmentSession).filter(
        TreatmentSession.treatment_plan_id.in_(plan_ids)
    ).order_by(TreatmentSession.scheduled_at.desc()).all()

    # Format sessions
    session_history = []
    for session in sessions:
        step = db.query(ProtocolStep).filter(ProtocolStep.id == session.protocol_step_id).first()

        # Get documentation if exists
        documentation = db.query(SessionDocumentation).filter(
            SessionDocumentation.treatment_session_id == session.id
        ).first()

        doc_dict = None
        vitals_list = None
        if documentation:
            doc_dict = {
                "therapist_notes": documentation.therapist_notes,
                "patient_subjective_notes": documentation.patient_subjective_notes,
                "clinical_scales": documentation.clinical_scales,
                "adverse_events": documentation.adverse_events
            }
            vitals_list = documentation.vitals

        session_history.append(SessionDetailResponse(
            id=session.id,
            treatment_plan_id=session.treatment_plan_id,
            protocol_step_id=session.protocol_step_id,
            scheduled_at=session.scheduled_at,
            actual_start=session.actual_start,
            actual_end=session.actual_end,
            status=session.status.value,
            location=session.location,
            therapist_id=session.therapist_id,
            patient_id=patient_id,
            patient_email=patient.email,
            step_title=step.title if step else "Unknown Step",
            step_description=step.description if step else None,
            vitals=vitals_list,
            documentation=doc_dict
        ))

    # Format treatment plans
    formatted_plans = []
    for plan in treatment_plans:
        formatted_plans.append(TreatmentPlanResponse(
            id=plan.id,
            patient_id=plan.patient_id,
            therapist_id=plan.therapist_id,
            clinic_id=plan.clinic_id,
            protocol_id=plan.protocol_id,
            protocol_version=plan.protocol_version,
            status=plan.status.value,
            start_date=plan.start_date,
            estimated_completion=plan.estimated_completion,
            customizations=plan.customizations,
            created_at=plan.created_at
        ))

    return PatientDetailResponse(
        id=patient.id,
        email=patient.email,
        full_name=patient.email.split('@')[0].replace('.', ' ').title(),
        date_of_birth=patient_profile.date_of_birth if patient_profile else None,
        medical_history=patient_profile.medical_history if patient_profile else None,
        medications=patient_profile.medications if patient_profile else None,
        contraindications=patient_profile.contraindications if patient_profile else None,
        treatment_plans=formatted_plans,
        session_history=session_history
    )


@router.post("/treatment-plans", response_model=TreatmentPlanResponse, status_code=status.HTTP_201_CREATED)
def create_treatment_plan(
    plan_data: TreatmentPlanCreate,
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Create a new treatment plan for a patient.

    Args:
        plan_data: Treatment plan data
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        TreatmentPlanResponse: Created treatment plan

    Raises:
        HTTPException: If patient not found or protocol not found
    """
    # Verify patient exists
    patient = db.query(User).filter(
        and_(
            User.id == plan_data.patient_id,
            User.role == UserRole.PATIENT
        )
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Verify protocol exists
    from app.models.protocol import Protocol
    protocol = db.query(Protocol).filter(Protocol.id == plan_data.protocol_id).first()
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found"
        )

    # Get therapist's clinic if they have one
    therapist_profile = db.query(TherapistProfile).filter(
        TherapistProfile.user_id == current_user.id
    ).first()

    # Create treatment plan
    treatment_plan = TreatmentPlan(
        patient_id=plan_data.patient_id,
        therapist_id=current_user.id,
        clinic_id=therapist_profile.clinic_id if therapist_profile else None,
        protocol_id=plan_data.protocol_id,
        protocol_version=protocol.version,
        status=TreatmentStatus.ACTIVE,
        start_date=plan_data.start_date,
        customizations=plan_data.customizations
    )

    db.add(treatment_plan)
    db.commit()
    db.refresh(treatment_plan)

    return treatment_plan


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session_details(
    session_id: int,
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific session.

    Args:
        session_id: Session ID
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        SessionDetailResponse: Detailed session information
    """
    # Verify therapist owns this session
    session = verify_therapist_owns_session(current_user.id, session_id, db)

    # Get related data
    treatment_plan = db.query(TreatmentPlan).filter(
        TreatmentPlan.id == session.treatment_plan_id
    ).first()

    patient = db.query(User).filter(User.id == treatment_plan.patient_id).first()

    step = db.query(ProtocolStep).filter(ProtocolStep.id == session.protocol_step_id).first()

    # Get documentation if exists
    documentation = db.query(SessionDocumentation).filter(
        SessionDocumentation.treatment_session_id == session_id
    ).first()

    doc_dict = None
    vitals_list = None

    if documentation:
        doc_dict = {
            "therapist_notes": documentation.therapist_notes,
            "patient_subjective_notes": documentation.patient_subjective_notes,
            "clinical_scales": documentation.clinical_scales,
            "adverse_events": documentation.adverse_events
        }
        vitals_list = documentation.vitals

    return SessionDetailResponse(
        id=session.id,
        treatment_plan_id=session.treatment_plan_id,
        protocol_step_id=session.protocol_step_id,
        scheduled_at=session.scheduled_at,
        actual_start=session.actual_start,
        actual_end=session.actual_end,
        status=session.status.value,
        location=session.location,
        therapist_id=session.therapist_id,
        patient_id=treatment_plan.patient_id,
        patient_email=patient.email,
        step_title=step.title,
        step_description=step.description,
        vitals=vitals_list,
        documentation=doc_dict
    )


@router.post("/sessions/{session_id}/vitals", response_model=SessionVitalsResponse)
def log_session_vitals(
    session_id: int,
    vitals_data: SessionVitalsLog,
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Log vitals during a treatment session.

    Args:
        session_id: Session ID
        vitals_data: Vitals measurements
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        SessionVitalsResponse: Confirmation of vitals logged
    """
    # Verify therapist owns this session
    session = verify_therapist_owns_session(current_user.id, session_id, db)

    # Get or create session documentation
    documentation = db.query(SessionDocumentation).filter(
        SessionDocumentation.treatment_session_id == session_id
    ).first()

    if not documentation:
        documentation = SessionDocumentation(
            treatment_session_id=session_id,
            vitals=[],
            clinical_scales={},
            adverse_events=[]
        )
        db.add(documentation)
        db.flush()

    # Append new vitals to existing vitals array
    vitals_entry = {
        "blood_pressure": vitals_data.blood_pressure,
        "heart_rate": vitals_data.heart_rate,
        "temperature": vitals_data.temperature,
        "spo2": vitals_data.spo2,
        "timestamp": vitals_data.timestamp.isoformat(),
        "notes": vitals_data.notes
    }

    if documentation.vitals is None:
        documentation.vitals = []

    documentation.vitals.append(vitals_entry)
    documentation.updated_at = datetime.utcnow()

    db.commit()

    return SessionVitalsResponse(
        message="Vitals logged successfully",
        vitals_logged=len(documentation.vitals),
        session_id=session_id
    )


@router.get("/sessions/{session_id}/documentation", response_model=SessionDocumentationResponse)
def get_session_documentation(
    session_id: int,
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """Get session documentation."""
    session = verify_therapist_owns_session(current_user.id, session_id, db)

    documentation = db.query(SessionDocumentation).filter(
        SessionDocumentation.treatment_session_id == session_id
    ).first()

    if not documentation:
        return SessionDocumentationResponse(
            id=0,
            treatment_session_id=session_id,
            message="No documentation found"
        )

    return SessionDocumentationResponse(
        id=documentation.id,
        treatment_session_id=session_id,
        message="Documentation retrieved successfully"
    )


@router.post("/sessions/{session_id}/documentation", response_model=SessionDocumentationResponse)
def save_session_documentation(
    session_id: int,
    doc_data: SessionDocumentationCreate,
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Save or update session documentation (notes, clinical scales, adverse events).

    Args:
        session_id: Session ID
        doc_data: Documentation data
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        SessionDocumentationResponse: Confirmation of documentation saved
    """
    # Verify therapist owns this session
    session = verify_therapist_owns_session(current_user.id, session_id, db)

    # Get or create session documentation
    documentation = db.query(SessionDocumentation).filter(
        SessionDocumentation.treatment_session_id == session_id
    ).first()

    if not documentation:
        documentation = SessionDocumentation(
            treatment_session_id=session_id,
            vitals=[],
            clinical_scales={},
            adverse_events=[]
        )
        db.add(documentation)
        db.flush()

    # Update documentation fields
    if doc_data.therapist_notes is not None:
        documentation.therapist_notes = doc_data.therapist_notes

    if doc_data.patient_subjective_notes is not None:
        documentation.patient_subjective_notes = doc_data.patient_subjective_notes

    if doc_data.clinical_scales is not None:
        documentation.clinical_scales = doc_data.clinical_scales

    if doc_data.adverse_events is not None:
        documentation.adverse_events = doc_data.adverse_events

    documentation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(documentation)

    return SessionDocumentationResponse(
        id=documentation.id,
        treatment_session_id=session_id,
        message="Documentation saved successfully"
    )


@router.post("/sessions/{session_id}/complete", response_model=SessionCompleteResponse)
def complete_session(
    session_id: int,
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Mark a session as completed.

    Args:
        session_id: Session ID
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        SessionCompleteResponse: Updated session status

    Raises:
        HTTPException: If session is not in progress or already completed
    """
    # Verify therapist owns this session
    session = verify_therapist_owns_session(current_user.id, session_id, db)

    # Verify session is in appropriate state to complete
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already completed"
        )

    if session.status == SessionStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete a cancelled session"
        )

    # Update session status
    session.status = SessionStatus.COMPLETED
    session.actual_end = datetime.utcnow()

    if not session.actual_start:
        session.actual_start = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return SessionCompleteResponse(
        id=session.id,
        status=session.status.value,
        actual_end=session.actual_end,
        message="Session completed successfully"
    )


@router.post("/decision-points/{decision_point_id}/evaluate", response_model=DecisionPointResponse)
def evaluate_decision_point(
    decision_point_id: int,
    evaluation: DecisionPointEvaluation,
    current_user: User = Depends(require_role(UserRole.THERAPIST)),
    db: Session = Depends(get_db)
):
    """
    Evaluate a decision point in the treatment protocol.

    Args:
        decision_point_id: Protocol step ID of the decision point
        evaluation: Evaluation data
        current_user: Current authenticated therapist
        db: Database session

    Returns:
        DecisionPointResponse: Evaluation result

    Raises:
        HTTPException: If decision point not found or therapist doesn't own treatment plan
    """
    # Verify decision point exists and is a decision point step
    from app.models.protocol import StepType
    decision_step = db.query(ProtocolStep).filter(
        and_(
            ProtocolStep.id == decision_point_id,
            ProtocolStep.step_type == StepType.DECISION_POINT
        )
    ).first()

    if not decision_step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision point not found"
        )

    # Verify treatment plan belongs to this therapist
    treatment_plan = db.query(TreatmentPlan).filter(
        TreatmentPlan.id == evaluation.treatment_plan_id
    ).first()

    if not treatment_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treatment plan not found"
        )

    if treatment_plan.therapist_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to evaluate this treatment plan"
        )

    # Store the evaluation in the treatment plan's customizations
    if treatment_plan.customizations is None:
        treatment_plan.customizations = {}

    if "decision_point_evaluations" not in treatment_plan.customizations:
        treatment_plan.customizations["decision_point_evaluations"] = []

    evaluation_record = {
        "decision_point_id": decision_point_id,
        "evaluation_criteria": evaluation.evaluation_criteria,
        "recommendation": evaluation.recommendation,
        "notes": evaluation.notes,
        "evaluated_by": current_user.id,
        "evaluated_at": datetime.utcnow().isoformat()
    }

    treatment_plan.customizations["decision_point_evaluations"].append(evaluation_record)
    treatment_plan.updated_at = datetime.utcnow()

    db.commit()

    return DecisionPointResponse(
        decision_point_id=decision_point_id,
        treatment_plan_id=evaluation.treatment_plan_id,
        recommendation=evaluation.recommendation,
        evaluation_data=evaluation.evaluation_criteria,
        message="Decision point evaluated successfully",
        timestamp=datetime.utcnow()
    )
