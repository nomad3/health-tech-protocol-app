"""Tests for AI service.

This module tests the AIService class with mocked Anthropic API responses.
Tests cover:
- Protocol extraction from research text
- Patient education generation
- Clinical decision support
- Error handling and rate limiting
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.services.ai_service import AIService, AIServiceError, AIRateLimitError
from anthropic import APIError, RateLimitError


# Sample research text for protocol extraction
SAMPLE_RESEARCH_TEXT = """
Psilocybin for Treatment-Resistant Depression: A Phase 3 Clinical Trial Protocol

Background: This protocol describes a 12-week treatment program using psilocybin-assisted therapy
for treatment-resistant depression.

Protocol Design:
Week 1: Initial psychiatric evaluation (90 minutes) - MADRS, BDI-II scales administered
Week 2-3: Preparation sessions (2 x 60 minutes each) - psychoeducation and rapport building
Week 4: Dosing session (25mg psilocybin, 6-8 hours supervised)
Week 5-8: Integration sessions (4 x 60 minutes weekly)
Week 12: Follow-up assessment

Safety Screening:
Absolute contraindications:
- Active psychosis or schizophrenia
- Severe cardiovascular disease
- Pregnancy or breastfeeding

Relative contraindications:
- First-degree relative with psychotic disorder
- Current use of SSRI medications
- History of mania

Monitoring:
- Vital signs every 30 minutes during dosing
- MADRS at baseline, week 5, and week 12
- Adverse events recorded continuously

Evidence: Based on Carhart-Harris et al. 2021, Davis et al. 2020 phase 2 trials.
"""

SAMPLE_PROTOCOL_EXTRACTION_RESPONSE = {
    "protocol": {
        "name": "Psilocybin for Treatment-Resistant Depression",
        "version": "1.0",
        "therapy_type": "psilocybin",
        "condition_treated": "treatment_resistant_depression",
        "evidence_level": "phase_3_trial",
        "overview": "12-week treatment program using psilocybin-assisted therapy",
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
        },
        {
            "sequence_order": 2,
            "step_type": "preparation",
            "title": "Preparation Session 1",
            "description": "Psychoeducation and rapport building",
            "duration_minutes": 60,
            "required_roles": ["therapist"]
        }
    ],
    "safety_checks": [
        {
            "step_sequence": 1,
            "check_type": "absolute_contraindication",
            "condition": {"field": "medical_history", "contains": "active_psychosis"},
            "severity": "blocking",
            "override_allowed": "false",
            "evidence_source": "Protocol safety guidelines"
        }
    ]
}


@pytest.fixture
def ai_service():
    """Create AI service instance for testing."""
    return AIService()


@pytest.fixture
def mock_anthropic_response():
    """Create a mock Anthropic API response."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(SAMPLE_PROTOCOL_EXTRACTION_RESPONSE))]
    mock_response.usage = MagicMock(input_tokens=1000, output_tokens=500)
    return mock_response


class TestProtocolExtraction:
    """Test protocol extraction from research text."""

    @patch('app.services.ai_service.Anthropic')
    def test_extract_protocol_from_text_success(self, mock_anthropic_class, ai_service, mock_anthropic_response):
        """Test successful protocol extraction."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_response
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Call service
        result = ai_service.extract_protocol_from_text(
            research_text=SAMPLE_RESEARCH_TEXT,
            therapy_type="psilocybin",
            condition="treatment_resistant_depression"
        )

        # Verify result structure
        assert "extracted_protocol" in result
        assert "steps" in result
        assert "safety_checks" in result
        assert "extraction_confidence" in result

        # Verify protocol data
        assert result["extracted_protocol"]["name"] == "Psilocybin for Treatment-Resistant Depression"
        assert result["extracted_protocol"]["therapy_type"] == "psilocybin"
        assert result["extracted_protocol"]["duration_weeks"] == 12

        # Verify steps
        assert len(result["steps"]) == 2
        assert result["steps"][0]["step_type"] == "screening"
        assert result["steps"][1]["step_type"] == "preparation"

        # Verify safety checks
        assert len(result["safety_checks"]) == 1
        assert result["safety_checks"][0]["severity"] == "blocking"

        # Verify API was called
        mock_client.messages.create.assert_called_once()

    @patch('app.services.ai_service.Anthropic')
    def test_extract_protocol_with_json_markdown(self, mock_anthropic_class, ai_service):
        """Test extraction when response is wrapped in markdown code blocks."""
        # Setup mock with markdown-wrapped JSON
        mock_client = MagicMock()
        json_text = json.dumps(SAMPLE_PROTOCOL_EXTRACTION_RESPONSE)
        wrapped_text = f"```json\n{json_text}\n```"
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=wrapped_text)]
        mock_response.usage = MagicMock(input_tokens=1000, output_tokens=500)
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Call service
        result = ai_service.extract_protocol_from_text(
            research_text=SAMPLE_RESEARCH_TEXT,
            therapy_type="psilocybin",
            condition="depression"
        )

        # Should successfully parse despite markdown wrapping
        assert result["extracted_protocol"]["name"] == "Psilocybin for Treatment-Resistant Depression"

    @patch('app.services.ai_service.Anthropic')
    def test_extract_protocol_rate_limit_error(self, mock_anthropic_class, ai_service):
        """Test handling of rate limit errors."""
        # Setup mock to raise RateLimitError
        mock_client = MagicMock()
        # Create a proper RateLimitError with required parameters
        mock_response = MagicMock()
        mock_response.status_code = 429
        rate_limit_error = RateLimitError(
            message="Rate limit exceeded",
            response=mock_response,
            body={"error": "rate_limit"}
        )
        mock_client.messages.create.side_effect = rate_limit_error
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Should raise AIRateLimitError
        with pytest.raises(AIRateLimitError, match="rate limit exceeded"):
            ai_service.extract_protocol_from_text(
                research_text=SAMPLE_RESEARCH_TEXT,
                therapy_type="psilocybin",
                condition="depression"
            )

    @patch('app.services.ai_service.Anthropic')
    def test_extract_protocol_api_error(self, mock_anthropic_class, ai_service):
        """Test handling of API errors."""
        # Setup mock to raise APIError
        mock_client = MagicMock()
        # Create a proper APIError with required parameters
        mock_request = MagicMock()
        api_error = APIError(message="API error occurred", request=mock_request, body=None)
        mock_client.messages.create.side_effect = api_error
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Should raise AIServiceError
        with pytest.raises(AIServiceError, match="AI service error"):
            ai_service.extract_protocol_from_text(
                research_text=SAMPLE_RESEARCH_TEXT,
                therapy_type="psilocybin",
                condition="depression"
            )

    @patch('app.services.ai_service.Anthropic')
    def test_extract_protocol_invalid_json(self, mock_anthropic_class, ai_service):
        """Test handling of invalid JSON in response."""
        # Setup mock with invalid JSON
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is not valid JSON")]
        mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Should raise AIServiceError for JSON parsing failure
        with pytest.raises(AIServiceError, match="Failed to parse AI response as JSON"):
            ai_service.extract_protocol_from_text(
                research_text=SAMPLE_RESEARCH_TEXT,
                therapy_type="psilocybin",
                condition="depression"
            )


class TestPatientEducationGeneration:
    """Test patient education content generation."""

    @patch('app.services.ai_service.Anthropic')
    def test_generate_patient_education_success(self, mock_anthropic_class, ai_service):
        """Test successful patient education generation."""
        # Sample education content
        education_content = """## Your Treatment Journey

We're glad you're here and taking this important step...

### What to Expect

Over the next 12 weeks, you'll participate in a carefully structured program...

### Timeline

- **Week 1**: Initial evaluation
- **Weeks 2-3**: Preparation sessions
- **Week 4**: Treatment session
"""

        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=education_content)]
        mock_response.usage = MagicMock(input_tokens=500, output_tokens=300)
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Call service
        result = ai_service.generate_patient_education(
            protocol_name="Psilocybin for Depression",
            condition="treatment_resistant_depression",
            patient_context={
                "anxiety_level": "high",
                "age_range": "adult",
                "education_level": "general"
            }
        )

        # Verify result structure
        assert "education_text" in result
        assert "word_count" in result
        assert "reading_time_minutes" in result
        assert "generated_at" in result

        # Verify content
        assert result["education_text"] == education_content
        assert result["word_count"] > 0
        assert result["reading_time_minutes"] > 0

        # Verify API was called
        mock_client.messages.create.assert_called_once()

    @patch('app.services.ai_service.Anthropic')
    def test_generate_patient_education_personalization(self, mock_anthropic_class, ai_service):
        """Test that patient context is used in prompt."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Education content")]
        mock_response.usage = MagicMock(input_tokens=500, output_tokens=300)
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Call with different anxiety levels
        contexts = [
            {"anxiety_level": "low", "age_range": "adult", "education_level": "general"},
            {"anxiety_level": "high", "age_range": "senior", "education_level": "medical"},
        ]

        for context in contexts:
            ai_service.generate_patient_education(
                protocol_name="Test Protocol",
                condition="test_condition",
                patient_context=context
            )

        # Verify API was called twice
        assert mock_client.messages.create.call_count == 2


class TestClinicalDecisionSupport:
    """Test clinical decision support."""

    @patch('app.services.ai_service.Anthropic')
    def test_clinical_decision_support_success(self, mock_anthropic_class, ai_service):
        """Test successful clinical decision support."""
        # Sample decision support response
        decision_response = {
            "risk_level": "low",
            "risk_factors": [],
            "recommendations": [
                {
                    "category": "monitoring",
                    "priority": "medium",
                    "action": "Continue standard monitoring",
                    "rationale": "Patient showing good progress",
                    "evidence_basis": "Protocol section 4.2"
                }
            ],
            "decision_point_evaluation": {
                "meets_continuation_criteria": True,
                "reasons": ["MADRS below threshold", "No adverse events"],
                "suggested_next_step": "Proceed to integration"
            },
            "clinical_notes": "Patient stable with good clinical progress.",
            "requires_immediate_attention": False,
            "suggested_interventions": []
        }

        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(decision_response))]
        mock_response.usage = MagicMock(input_tokens=800, output_tokens=400)
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Call service
        session_data = {
            "session_id": 5,
            "step_sequence": 3,
            "vitals": {"heart_rate": 78, "blood_pressure_systolic": 125},
            "adverse_events": [],
            "clinical_scales": {"MADRS": 15}
        }
        protocol_context = {
            "protocol_name": "Test Protocol",
            "current_step_title": "Integration Session",
            "step_type": "integration"
        }
        patient_history = {
            "baseline_measures": {"MADRS": 32},
            "previous_sessions": [],
            "risk_factors": []
        }

        result = ai_service.provide_clinical_decision_support(
            session_data=session_data,
            protocol_context=protocol_context,
            patient_history=patient_history
        )

        # Verify result structure
        assert result["risk_level"] == "low"
        assert len(result["recommendations"]) == 1
        assert result["requires_immediate_attention"] is False
        assert result["decision_point_evaluation"]["meets_continuation_criteria"] is True

        # Verify API was called
        mock_client.messages.create.assert_called_once()

    @patch('app.services.ai_service.Anthropic')
    def test_clinical_decision_support_critical_risk(self, mock_anthropic_class, ai_service):
        """Test clinical decision support with critical risk level."""
        # Critical risk response
        decision_response = {
            "risk_level": "critical",
            "risk_factors": [
                {
                    "factor": "Severe hypertension detected",
                    "severity": "urgent",
                    "recommendation": "Immediate medical evaluation required"
                }
            ],
            "recommendations": [
                {
                    "category": "safety",
                    "priority": "high",
                    "action": "Stop session and seek medical evaluation",
                    "rationale": "BP exceeds safety thresholds",
                    "evidence_basis": "Safety protocol section 2.1"
                }
            ],
            "clinical_notes": "URGENT: Patient requires immediate medical attention.",
            "requires_immediate_attention": True,
            "suggested_interventions": ["Transfer to medical facility"]
        }

        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(decision_response))]
        mock_response.usage = MagicMock(input_tokens=800, output_tokens=400)
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        ai_service.client = mock_client

        # Call service
        result = ai_service.provide_clinical_decision_support(
            session_data={"session_id": 1, "step_sequence": 1, "vitals": {"blood_pressure_systolic": 200}},
            protocol_context={"protocol_name": "Test", "current_step_title": "Dosing", "step_type": "dosing"},
            patient_history={"baseline_measures": {}, "previous_sessions": [], "risk_factors": []}
        )

        # Verify critical flags
        assert result["risk_level"] == "critical"
        assert result["requires_immediate_attention"] is True
        assert len(result["risk_factors"]) > 0
        assert result["risk_factors"][0]["severity"] == "urgent"


class TestValidation:
    """Test extraction validation logic."""

    def test_validate_extraction_complete(self, ai_service):
        """Test validation with complete extraction."""
        extracted_data = {
            "protocol": {
                "name": "Test Protocol",
                "duration_weeks": 12,
                "total_sessions": 8
            },
            "steps": [
                {"sequence_order": 1, "step_type": "screening", "title": "Screening"},
                {"sequence_order": 2, "step_type": "preparation", "title": "Prep"},
                {"sequence_order": 3, "step_type": "dosing", "title": "Dosing"}
            ],
            "safety_checks": [
                {"check_type": "absolute_contraindication", "severity": "blocking"}
            ]
        }

        warnings = ai_service._validate_extraction(extracted_data)
        assert warnings is None  # No warnings for complete data

    def test_validate_extraction_missing_protocol_fields(self, ai_service):
        """Test validation with missing protocol fields."""
        extracted_data = {
            "protocol": {},  # Missing required fields
            "steps": [{"sequence_order": 1, "step_type": "screening", "title": "Screening"}],
            "safety_checks": []
        }

        warnings = ai_service._validate_extraction(extracted_data)
        assert warnings is not None
        assert any("name is missing" in w for w in warnings)
        assert any("Duration not specified" in w for w in warnings)

    def test_validate_extraction_no_screening_step(self, ai_service):
        """Test validation warns about missing screening step."""
        extracted_data = {
            "protocol": {"name": "Test", "duration_weeks": 12, "total_sessions": 2},
            "steps": [
                {"sequence_order": 1, "step_type": "preparation", "title": "Prep"},
                {"sequence_order": 2, "step_type": "dosing", "title": "Dosing"}
            ],
            "safety_checks": []
        }

        warnings = ai_service._validate_extraction(extracted_data)
        assert warnings is not None
        assert any("No screening step found" in w for w in warnings)

    def test_validate_extraction_no_safety_checks(self, ai_service):
        """Test validation warns about missing safety checks."""
        extracted_data = {
            "protocol": {"name": "Test", "duration_weeks": 12, "total_sessions": 3},
            "steps": [
                {"sequence_order": 1, "step_type": "screening", "title": "Screening"},
                {"sequence_order": 2, "step_type": "preparation", "title": "Prep"},
                {"sequence_order": 3, "step_type": "dosing", "title": "Dosing"}
            ],
            "safety_checks": []  # No safety checks
        }

        warnings = ai_service._validate_extraction(extracted_data)
        assert warnings is not None
        assert any("No safety checks extracted" in w for w in warnings)
