"""Tests for AI API endpoints.

This module tests the AI integration API endpoints:
- POST /api/v1/ai/extract-protocol
- POST /api/v1/ai/generate-patient-education
- POST /api/v1/ai/decision-support

Tests include authorization, validation, and error handling.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.services.ai_service import AIServiceError, AIRateLimitError


# Create test database tables
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db_session):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# Sample data for tests
SAMPLE_EXTRACTION_REQUEST = {
    "research_text": "Clinical protocol for psilocybin therapy...\n" * 50,  # Make it long enough
    "therapy_type": "psilocybin",
    "condition": "treatment_resistant_depression"
}

SAMPLE_EXTRACTION_RESPONSE = {
    "extracted_protocol": {
        "name": "Psilocybin for Depression",
        "version": "1.0",
        "therapy_type": "psilocybin",
        "condition_treated": "treatment_resistant_depression",
        "evidence_level": "phase_3_trial",
        "overview": "Test protocol",
        "duration_weeks": 12,
        "total_sessions": 8
    },
    "steps": [
        {
            "sequence_order": 1,
            "step_type": "screening",
            "title": "Initial Evaluation",
            "duration_minutes": 90
        }
    ],
    "safety_checks": [],
    "extraction_confidence": 0.92,
    "warnings": None
}

SAMPLE_EDUCATION_REQUEST = {
    "protocol_id": 1,
    "protocol_name": "Psilocybin for Depression",
    "condition": "treatment_resistant_depression",
    "patient_context": {
        "anxiety_level": "moderate",
        "age_range": "adult",
        "education_level": "general"
    }
}

SAMPLE_EDUCATION_RESPONSE = {
    "education_text": "## Your Treatment Journey\n\nWelcome...",
    "word_count": 1200,
    "reading_time_minutes": 6,
    "generated_at": "2025-11-16T10:00:00Z"
}

SAMPLE_DECISION_REQUEST = {
    "session_data": {
        "session_id": 5,
        "step_sequence": 3,
        "vitals": {"heart_rate": 78, "blood_pressure_systolic": 125},
        "adverse_events": [],
        "clinical_scales": {"MADRS": 15}
    },
    "protocol_context": {
        "protocol_name": "Psilocybin for Depression",
        "current_step_title": "Integration Session",
        "step_type": "integration"
    },
    "patient_history": {
        "baseline_measures": {"MADRS": 32},
        "previous_sessions": [],
        "risk_factors": [],
        "medications": []
    }
}

SAMPLE_DECISION_RESPONSE = {
    "risk_level": "low",
    "risk_factors": [],
    "recommendations": [
        {
            "category": "monitoring",
            "priority": "medium",
            "action": "Continue monitoring",
            "rationale": "Good progress",
            "evidence_basis": "Protocol 4.2"
        }
    ],
    "decision_point_evaluation": {
        "meets_continuation_criteria": True,
        "reasons": ["MADRS improved"],
        "suggested_next_step": "Continue treatment"
    },
    "clinical_notes": "Patient stable",
    "requires_immediate_attention": False,
    "suggested_interventions": [],
    "confidence_score": 0.90
}


@pytest.fixture
def admin_token(db_session):
    """Create an admin user and return auth token."""
    import uuid
    from app.core.security import hash_password, create_access_token

    # Create admin user with unique email
    unique_email = f"admin-{uuid.uuid4()}@test.com"
    admin = User(
        email=unique_email,
        password_hash=hash_password("password"),
        role=UserRole.PLATFORM_ADMIN,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()

    # Create token
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    return token


@pytest.fixture
def therapist_token(db_session):
    """Create a therapist user and return auth token."""
    import uuid
    from app.core.security import hash_password, create_access_token

    # Create therapist user with unique email
    unique_email = f"therapist-{uuid.uuid4()}@test.com"
    therapist = User(
        email=unique_email,
        password_hash=hash_password("password"),
        role=UserRole.THERAPIST,
        is_active=True
    )
    db_session.add(therapist)
    db_session.commit()

    # Create token
    token = create_access_token({"sub": therapist.email, "role": therapist.role.value})
    return token


@pytest.fixture
def patient_token(db_session):
    """Create a patient user and return auth token."""
    import uuid
    from app.core.security import hash_password, create_access_token

    # Create patient user with unique email
    unique_email = f"patient-{uuid.uuid4()}@test.com"
    patient = User(
        email=unique_email,
        password_hash=hash_password("password"),
        role=UserRole.PATIENT,
        is_active=True
    )
    db_session.add(patient)
    db_session.commit()

    # Create token
    token = create_access_token({"sub": patient.email, "role": patient.role.value})
    return token


class TestProtocolExtractionEndpoint:
    """Test POST /api/v1/ai/extract-protocol endpoint."""

    @patch('app.services.ai_service.ai_service.extract_protocol_from_text')
    def test_extract_protocol_success_as_admin(self, mock_extract, admin_token, client, db_session):
        """Test successful protocol extraction as admin."""
        # Mock AI service response
        mock_extract.return_value = SAMPLE_EXTRACTION_RESPONSE

        # Make request
        response = client.post(
            "/api/v1/ai/extract-protocol",
            json=SAMPLE_EXTRACTION_REQUEST,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "extracted_protocol" in data
        assert data["extracted_protocol"]["name"] == "Psilocybin for Depression"
        assert "steps" in data
        assert "extraction_confidence" in data

        # Verify AI service was called
        mock_extract.assert_called_once()

    @patch('app.services.ai_service.ai_service.extract_protocol_from_text')
    def test_extract_protocol_unauthorized_as_patient(self, mock_extract, patient_token, client):
        """Test that patients cannot extract protocols."""
        response = client.post(
            "/api/v1/ai/extract-protocol",
            json=SAMPLE_EXTRACTION_REQUEST,
            headers={"Authorization": f"Bearer {patient_token}"}
        )

        # Should be forbidden
        assert response.status_code == 403
        mock_extract.assert_not_called()

    def test_extract_protocol_no_auth(self, client):
        """Test that authentication is required."""
        response = client.post(
            "/api/v1/ai/extract-protocol",
            json=SAMPLE_EXTRACTION_REQUEST
        )

        # Should be unauthorized
        assert response.status_code == 403  # FastAPI returns 403 for missing bearer token

    @patch('app.services.ai_service.ai_service.extract_protocol_from_text')
    def test_extract_protocol_validation_error(self, mock_extract, admin_token, client):
        """Test validation of request data."""
        # Invalid request - text too short
        invalid_request = {
            "research_text": "Too short",
            "therapy_type": "psilocybin",
            "condition": "depression"
        }

        response = client.post(
            "/api/v1/ai/extract-protocol",
            json=invalid_request,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Should return validation error
        assert response.status_code == 422
        mock_extract.assert_not_called()

    @patch('app.services.ai_service.ai_service.extract_protocol_from_text')
    def test_extract_protocol_rate_limit_error(self, mock_extract, admin_token, client, db_session):
        """Test handling of rate limit errors."""
        # Mock AI service to raise rate limit error
        mock_extract.side_effect = AIRateLimitError("Rate limit exceeded")

        response = client.post(
            "/api/v1/ai/extract-protocol",
            json=SAMPLE_EXTRACTION_REQUEST,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Should return 429 Too Many Requests
        assert response.status_code == 429
        assert "rate limit" in response.json()["detail"].lower()

    @patch('app.services.ai_service.ai_service.extract_protocol_from_text')
    def test_extract_protocol_service_error(self, mock_extract, admin_token, client, db_session):
        """Test handling of AI service errors."""
        # Mock AI service to raise service error
        mock_extract.side_effect = AIServiceError("Service unavailable")

        response = client.post(
            "/api/v1/ai/extract-protocol",
            json=SAMPLE_EXTRACTION_REQUEST,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Should return 503 Service Unavailable
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()


class TestPatientEducationEndpoint:
    """Test POST /api/v1/ai/generate-patient-education endpoint."""

    @patch('app.services.ai_service.ai_service.generate_patient_education')
    def test_generate_education_success(self, mock_generate, patient_token, client, db_session):
        """Test successful education generation as patient."""
        # Mock AI service response
        mock_generate.return_value = SAMPLE_EDUCATION_RESPONSE

        # Make request
        response = client.post(
            "/api/v1/ai/generate-patient-education",
            json=SAMPLE_EDUCATION_REQUEST,
            headers={"Authorization": f"Bearer {patient_token}"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "education_text" in data
        assert "word_count" in data
        assert data["word_count"] == 1200

        # Verify AI service was called
        mock_generate.assert_called_once()

    @patch('app.services.ai_service.ai_service.generate_patient_education')
    def test_generate_education_as_therapist(self, mock_generate, therapist_token, client, db_session):
        """Test that therapists can also generate education content."""
        mock_generate.return_value = SAMPLE_EDUCATION_RESPONSE

        response = client.post(
            "/api/v1/ai/generate-patient-education",
            json=SAMPLE_EDUCATION_REQUEST,
            headers={"Authorization": f"Bearer {therapist_token}"}
        )

        # Should succeed
        assert response.status_code == 200
        mock_generate.assert_called_once()

    def test_generate_education_no_auth(self, client):
        """Test that authentication is required."""
        response = client.post(
            "/api/v1/ai/generate-patient-education",
            json=SAMPLE_EDUCATION_REQUEST
        )

        # Should be unauthorized
        assert response.status_code == 403

    @patch('app.services.ai_service.ai_service.generate_patient_education')
    def test_generate_education_validation_error(self, mock_generate, patient_token, client):
        """Test validation of request data."""
        # Invalid request - missing required fields
        invalid_request = {
            "protocol_id": 1
            # Missing protocol_name and condition
        }

        response = client.post(
            "/api/v1/ai/generate-patient-education",
            json=invalid_request,
            headers={"Authorization": f"Bearer {patient_token}"}
        )

        # Should return validation error
        assert response.status_code == 422
        mock_generate.assert_not_called()

    @patch('app.services.ai_service.ai_service.generate_patient_education')
    def test_generate_education_with_custom_context(self, mock_generate, patient_token, client, db_session):
        """Test generation with custom patient context."""
        mock_generate.return_value = SAMPLE_EDUCATION_RESPONSE

        # Request with high anxiety patient
        custom_request = {
            **SAMPLE_EDUCATION_REQUEST,
            "patient_context": {
                "anxiety_level": "high",
                "age_range": "senior",
                "education_level": "medical"
            }
        }

        response = client.post(
            "/api/v1/ai/generate-patient-education",
            json=custom_request,
            headers={"Authorization": f"Bearer {patient_token}"}
        )

        # Should succeed
        assert response.status_code == 200

        # Verify the service was called with the custom context
        call_args = mock_generate.call_args
        assert call_args[1]["patient_context"]["anxiety_level"] == "high"


class TestClinicalDecisionSupportEndpoint:
    """Test POST /api/v1/ai/decision-support endpoint."""

    @patch('app.services.ai_service.ai_service.provide_clinical_decision_support')
    def test_decision_support_success_as_therapist(self, mock_support, therapist_token, client, db_session):
        """Test successful decision support as therapist."""
        # Mock AI service response
        mock_support.return_value = SAMPLE_DECISION_RESPONSE

        # Make request
        response = client.post(
            "/api/v1/ai/decision-support",
            json=SAMPLE_DECISION_REQUEST,
            headers={"Authorization": f"Bearer {therapist_token}"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "low"
        assert "recommendations" in data
        assert "decision_point_evaluation" in data

        # Verify AI service was called
        mock_support.assert_called_once()

    @patch('app.services.ai_service.ai_service.provide_clinical_decision_support')
    def test_decision_support_unauthorized_as_patient(self, mock_support, patient_token, client):
        """Test that patients cannot access decision support."""
        response = client.post(
            "/api/v1/ai/decision-support",
            json=SAMPLE_DECISION_REQUEST,
            headers={"Authorization": f"Bearer {patient_token}"}
        )

        # Should be forbidden
        assert response.status_code == 403
        mock_support.assert_not_called()

    @patch('app.services.ai_service.ai_service.provide_clinical_decision_support')
    def test_decision_support_critical_risk(self, mock_support, therapist_token, client, db_session):
        """Test decision support with critical risk level."""
        # Mock critical risk response
        critical_response = {
            **SAMPLE_DECISION_RESPONSE,
            "risk_level": "critical",
            "requires_immediate_attention": True,
            "risk_factors": [
                {
                    "factor": "Severe hypertension",
                    "severity": "urgent",
                    "recommendation": "Immediate medical evaluation"
                }
            ]
        }
        mock_support.return_value = critical_response

        response = client.post(
            "/api/v1/ai/decision-support",
            json=SAMPLE_DECISION_REQUEST,
            headers={"Authorization": f"Bearer {therapist_token}"}
        )

        # Should succeed with critical warning
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "critical"
        assert data["requires_immediate_attention"] is True

    @patch('app.services.ai_service.ai_service.provide_clinical_decision_support')
    def test_decision_support_validation_error(self, mock_support, therapist_token, client):
        """Test validation of request data."""
        # Invalid request - missing required fields
        invalid_request = {
            "session_data": {
                "session_id": 5
                # Missing other required fields
            }
        }

        response = client.post(
            "/api/v1/ai/decision-support",
            json=invalid_request,
            headers={"Authorization": f"Bearer {therapist_token}"}
        )

        # Should return validation error
        assert response.status_code == 422
        mock_support.assert_not_called()


class TestAuditLogging:
    """Test that AI interactions are properly logged."""

    @patch('app.services.ai_service.ai_service.extract_protocol_from_text')
    @patch('app.services.audit_service.AuditService.log_ai_interaction')
    def test_protocol_extraction_logged(self, mock_log, mock_extract, admin_token, client, db_session):
        """Test that protocol extraction is logged to audit trail."""
        mock_extract.return_value = SAMPLE_EXTRACTION_RESPONSE

        response = client.post(
            "/api/v1/ai/extract-protocol",
            json=SAMPLE_EXTRACTION_REQUEST,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200

        # Verify audit logging was called
        mock_log.assert_called_once()
        call_args = mock_log.call_args[1]
        assert call_args["action"] == "protocol_extraction"
        assert "therapy_type" in call_args["input_data"]

    @patch('app.services.ai_service.ai_service.generate_patient_education')
    @patch('app.services.audit_service.AuditService.log_ai_interaction')
    def test_education_generation_logged(self, mock_log, mock_generate, patient_token, client, db_session):
        """Test that education generation is logged."""
        mock_generate.return_value = SAMPLE_EDUCATION_RESPONSE

        response = client.post(
            "/api/v1/ai/generate-patient-education",
            json=SAMPLE_EDUCATION_REQUEST,
            headers={"Authorization": f"Bearer {patient_token}"}
        )

        assert response.status_code == 200

        # Verify audit logging
        mock_log.assert_called_once()
        call_args = mock_log.call_args[1]
        assert call_args["action"] == "patient_education_generation"

    @patch('app.services.ai_service.ai_service.provide_clinical_decision_support')
    @patch('app.services.audit_service.AuditService.log_ai_interaction')
    def test_decision_support_logged(self, mock_log, mock_support, therapist_token, client, db_session):
        """Test that decision support is logged."""
        mock_support.return_value = SAMPLE_DECISION_RESPONSE

        response = client.post(
            "/api/v1/ai/decision-support",
            json=SAMPLE_DECISION_REQUEST,
            headers={"Authorization": f"Bearer {therapist_token}"}
        )

        assert response.status_code == 200

        # Verify audit logging
        mock_log.assert_called_once()
        call_args = mock_log.call_args[1]
        assert call_args["action"] == "clinical_decision_support"
