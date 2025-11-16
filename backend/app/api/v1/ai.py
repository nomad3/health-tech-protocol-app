"""AI integration API endpoints.

This module provides endpoints for:
- Protocol extraction from research text (admin only)
- Patient education content generation (authenticated users)
- Clinical decision support (therapists and medical directors only)

All AI interactions are rate-limited and logged for audit purposes.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.api.dependencies import get_current_user, require_role
from app.services.ai_service import ai_service, AIServiceError, AIRateLimitError
from app.services.audit_service import AuditService
from app.schemas.ai import (
    ProtocolExtractionRequest,
    ProtocolExtractionResponse,
    PatientEducationRequest,
    PatientEducationResponse,
    ClinicalDecisionRequest,
    ClinicalDecisionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])


@router.post(
    "/extract-protocol",
    response_model=ProtocolExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract protocol from research text",
    description="Uses Claude AI to extract structured protocol from research papers or clinical guidelines. Admin only.",
)
async def extract_protocol(
    request: ProtocolExtractionRequest,
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN, UserRole.MEDICAL_DIRECTOR)),
    db: Session = Depends(get_db),
):
    """
    Extract a structured protocol from research text using AI.

    **Required Role:** Platform Admin or Medical Director

    **Process:**
    1. Validates research text length and content
    2. Calls Claude API with protocol extraction prompt
    3. Parses and validates extracted protocol structure
    4. Returns structured protocol ready for review and import

    **Important:**
    - This is an AI-assisted tool - all extractions must be reviewed by medical staff
    - The extracted protocol will be in draft status and require approval
    - Safety checks should be manually verified against source material
    - Evidence sources should be cross-referenced

    **Rate Limits:**
    - 10 requests per hour per user
    - Maximum text length: 50,000 characters
    """
    try:
        logger.info(
            f"Protocol extraction requested by user {current_user.id} - "
            f"Therapy: {request.therapy_type}, Condition: {request.condition}"
        )

        # Call AI service
        result = ai_service.extract_protocol_from_text(
            research_text=request.research_text,
            therapy_type=request.therapy_type,
            condition=request.condition
        )

        # Log to audit
        audit_svc = AuditService(db)
        audit_svc.log_ai_interaction(
            db=db,
            user_id=current_user.id,
            action="protocol_extraction",
            input_data={
                "therapy_type": request.therapy_type,
                "condition": request.condition,
                "text_length": len(request.research_text)
            },
            output_data={
                "protocol_name": result["extracted_protocol"].get("name"),
                "steps_count": len(result["steps"]),
                "confidence": result["extraction_confidence"]
            },
            metadata={
                "warnings": result.get("warnings"),
                "extraction_confidence": result["extraction_confidence"]
            }
        )

        logger.info(
            f"Protocol extraction successful - "
            f"User: {current_user.id}, Steps: {len(result['steps'])}"
        )

        return ProtocolExtractionResponse(**result)

    except AIRateLimitError as e:
        logger.warning(f"Rate limit exceeded for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )

    except AIServiceError as e:
        logger.error(f"AI service error during protocol extraction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Unexpected error during protocol extraction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post(
    "/generate-patient-education",
    response_model=PatientEducationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate patient education content",
    description="Generates personalized, compassionate patient education content for a treatment protocol.",
)
async def generate_patient_education(
    request: PatientEducationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate personalized patient education content.

    **Required Role:** Any authenticated user

    **Personalization Factors:**
    - Anxiety level (low/moderate/high) - adjusts tone and detail
    - Age range (young_adult/adult/senior) - adjusts language complexity
    - Education level (general/technical/medical) - adjusts terminology

    **Content Includes:**
    - Treatment overview and timeline
    - What to expect at each phase
    - Preparation tips
    - Safety and support information
    - Integration and follow-up guidance

    **Important:**
    - Content is generated fresh for each request
    - May be cached for performance (check generated_at timestamp)
    - Should be reviewed by clinical staff before sharing with patients
    - Does not replace individual clinical consultation

    **Rate Limits:**
    - 20 requests per hour per user
    """
    try:
        logger.info(
            f"Patient education generation requested by user {current_user.id} - "
            f"Protocol: {request.protocol_name}"
        )

        # Call AI service
        result = ai_service.generate_patient_education(
            protocol_name=request.protocol_name,
            condition=request.condition,
            patient_context=request.patient_context.model_dump()
        )

        # Log to audit
        audit_svc = AuditService(db)
        audit_svc.log_ai_interaction(
            db=db,
            user_id=current_user.id,
            action="patient_education_generation",
            input_data={
                "protocol_id": request.protocol_id,
                "protocol_name": request.protocol_name,
                "patient_context": request.patient_context.model_dump()
            },
            output_data={
                "word_count": result["word_count"],
                "reading_time_minutes": result["reading_time_minutes"]
            },
            metadata={
                "generated_at": result["generated_at"]
            }
        )

        logger.info(
            f"Patient education generated - "
            f"User: {current_user.id}, Words: {result['word_count']}"
        )

        return PatientEducationResponse(**result)

    except AIRateLimitError as e:
        logger.warning(f"Rate limit exceeded for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )

    except AIServiceError as e:
        logger.error(f"AI service error during patient education generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Unexpected error during patient education generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post(
    "/decision-support",
    response_model=ClinicalDecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get clinical decision support",
    description="Provides real-time AI-powered clinical decision support during treatment sessions. Therapists only.",
)
async def get_clinical_decision_support(
    request: ClinicalDecisionRequest,
    current_user: User = Depends(require_role(
        UserRole.THERAPIST,
        UserRole.MEDICAL_DIRECTOR,
        UserRole.CLINIC_ADMIN
    )),
    db: Session = Depends(get_db),
):
    """
    Get real-time clinical decision support.

    **Required Role:** Therapist, Medical Director, or Clinic Admin

    **Analyzes:**
    - Current session vitals and clinical scales
    - Protocol compliance and progression
    - Patient history and risk factors
    - Decision point criteria

    **Provides:**
    - Overall risk assessment (low/moderate/high/critical)
    - Specific risk factors and recommendations
    - Decision point evaluation (if applicable)
    - Suggested interventions
    - Clinical notes for documentation

    **Important:**
    - This is DECISION SUPPORT, not decision making
    - Final clinical judgment rests with the licensed provider
    - All recommendations are evidence-based and cite sources
    - Conservative approach - flags borderline cases
    - Immediate attention flags trigger alerts

    **Safety:**
    - All decision support interactions are logged
    - Critical risk levels trigger additional logging
    - Cannot override safety checks
    - Recommends escalation to medical director when appropriate

    **Rate Limits:**
    - 50 requests per hour per user (higher limit for clinical use)
    """
    try:
        logger.info(
            f"Clinical decision support requested by user {current_user.id} - "
            f"Session: {request.session_data.session_id}, "
            f"Protocol: {request.protocol_context.protocol_name}"
        )

        # Call AI service
        result = ai_service.provide_clinical_decision_support(
            session_data=request.session_data.model_dump(),
            protocol_context=request.protocol_context.model_dump(),
            patient_history=request.patient_history.model_dump()
        )

        # Log to audit
        audit_svc = AuditService(db)
        audit_svc.log_ai_interaction(
            db=db,
            user_id=current_user.id,
            action="clinical_decision_support",
            input_data={
                "session_id": request.session_data.session_id,
                "step_sequence": request.session_data.step_sequence,
                "protocol_name": request.protocol_context.protocol_name
            },
            output_data={
                "risk_level": result["risk_level"],
                "recommendations_count": len(result["recommendations"]),
                "requires_immediate_attention": result["requires_immediate_attention"]
            },
            metadata={
                "confidence_score": result["confidence_score"],
                "decision_point_evaluation": result.get("decision_point_evaluation")
            }
        )

        # Additional logging for critical cases
        if result["risk_level"] == "critical" or result["requires_immediate_attention"]:
            logger.warning(
                f"CRITICAL DECISION SUPPORT - "
                f"User: {current_user.id}, "
                f"Session: {request.session_data.session_id}, "
                f"Risk: {result['risk_level']}, "
                f"Immediate attention: {result['requires_immediate_attention']}"
            )
            # Could trigger additional notifications here

        logger.info(
            f"Clinical decision support generated - "
            f"User: {current_user.id}, "
            f"Risk: {result['risk_level']}, "
            f"Recommendations: {len(result['recommendations'])}"
        )

        return ClinicalDecisionResponse(**result)

    except AIRateLimitError as e:
        logger.warning(f"Rate limit exceeded for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )

    except AIServiceError as e:
        logger.error(f"AI service error during clinical decision support: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Unexpected error during clinical decision support: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
