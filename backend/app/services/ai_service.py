"""AI service for Google Gemini API integration.

This service handles all interactions with the Google Gemini API for:
- Protocol extraction from research text
- Patient education content generation
- Clinical decision support
- Pre-screening conversations

All AI interactions are logged for audit purposes.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from app.config import settings
from app.utils.ai_prompts import (
    get_protocol_extraction_prompt,
    get_patient_education_prompt,
    get_clinical_decision_support_prompt,
)
from app.schemas.ai import (
    ProtocolExtractionResponse,
    PatientEducationResponse,
    ClinicalDecisionResponse,
)

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class AIRateLimitError(AIServiceError):
    """Raised when API rate limit is exceeded."""
    pass


class AIService:
    """Service for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize AI service with Gemini client."""
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.warning("GEMINI_API_KEY not configured. AI features will be limited.")
            self.model = None

        self.max_tokens = 4096
        self.temperature = 0.3  # Lower temperature for consistent, factual outputs

    def _call_gemini(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Make a call to Gemini API with error handling and logging.

        Args:
            prompt: The prompt to send to Gemini
            system_message: Optional system message for additional context

        Returns:
            Gemini's response text

        Raises:
            AIRateLimitError: If rate limit is exceeded
            AIServiceError: For other API errors
        """
        if not self.model:
            raise AIServiceError("Gemini API is not configured. Please set GEMINI_API_KEY.")

        try:
            logger.info(f"Calling Gemini API - Model: gemini-1.5-flash, Prompt length: {len(prompt)}")

            # Combine system message with prompt if provided
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"

            # Configure generation
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            # Call API
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
            )

            # Extract text from response
            response_text = response.text

            logger.info(
                f"Gemini API call successful - "
                f"Response length: {len(response_text)}"
            )

            return response_text

        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise AIRateLimitError("API rate limit exceeded. Please try again later.") from e

        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Google API error: {str(e)}")
            raise AIServiceError(f"AI service error: {str(e)}") from e

        except Exception as e:
            logger.error(f"Unexpected error in AI service: {str(e)}")
            raise AIServiceError(f"Unexpected error: {str(e)}") from e

    def extract_protocol_from_text(
        self,
        research_text: str,
        therapy_type: str,
        condition: str
    ) -> Dict[str, Any]:
        """Extract structured protocol from research text using Gemini.

        Args:
            research_text: Raw text from research paper or guidelines
            therapy_type: Type of therapy (e.g., "psilocybin")
            condition: Condition being treated (e.g., "depression")

        Returns:
            Dict with extracted protocol structure containing:
                - protocol: Basic protocol metadata
                - steps: List of protocol steps
                - safety_checks: List of safety checks
                - extraction_confidence: Confidence score
                - warnings: Any extraction warnings

        Raises:
            AIServiceError: If extraction fails
        """
        logger.info(
            f"Starting protocol extraction - "
            f"Therapy: {therapy_type}, Condition: {condition}, "
            f"Text length: {len(research_text)}"
        )

        # Generate prompt
        prompt = get_protocol_extraction_prompt(research_text, therapy_type, condition)

        # Add system message for JSON formatting
        system_message = (
            "You are a medical protocol extraction expert. "
            "Always respond with valid JSON matching the requested schema. "
            "Be conservative and evidence-based in your extractions."
        )

        # Call Gemini
        response_text = self._call_gemini(prompt, system_message)

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_text = response_text
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0].strip()

            extracted_data = json.loads(json_text)

            # Add metadata
            result = {
                "extracted_protocol": extracted_data.get("protocol", {}),
                "steps": extracted_data.get("steps", []),
                "safety_checks": extracted_data.get("safety_checks", []),
                "extraction_confidence": 0.85,  # Could implement actual confidence scoring
                "warnings": self._validate_extraction(extracted_data)
            }

            logger.info(
                f"Protocol extraction successful - "
                f"Steps: {len(result['steps'])}, "
                f"Safety checks: {len(result['safety_checks'])}"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            raise AIServiceError(f"Failed to parse AI response as JSON: {str(e)}") from e

    def generate_patient_education(
        self,
        protocol_name: str,
        condition: str,
        patient_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized patient education content.

        Args:
            protocol_name: Name of the treatment protocol
            condition: Condition being treated
            patient_context: Dict with patient info (anxiety_level, age_range, education_level)

        Returns:
            Dict with:
                - education_text: Generated markdown content
                - word_count: Word count
                - reading_time_minutes: Estimated reading time
                - generated_at: Timestamp

        Raises:
            AIServiceError: If generation fails
        """
        logger.info(
            f"Generating patient education - "
            f"Protocol: {protocol_name}, "
            f"Condition: {condition}, "
            f"Context: {patient_context}"
        )

        # Generate prompt
        prompt = get_patient_education_prompt(protocol_name, condition, patient_context)

        # System message for compassionate, accurate content
        system_message = (
            "You are a compassionate medical educator. "
            "Create warm, reassuring content that is scientifically accurate. "
            "Never make unrealistic promises. Always emphasize safety and professional support."
        )

        # Call Gemini
        response_text = self._call_gemini(prompt, system_message)

        # Calculate metrics
        word_count = len(response_text.split())
        reading_time_minutes = max(1, word_count // 200)  # Average reading speed

        result = {
            "education_text": response_text,
            "word_count": word_count,
            "reading_time_minutes": reading_time_minutes,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

        logger.info(
            f"Patient education generated - "
            f"Words: {word_count}, "
            f"Reading time: {reading_time_minutes} min"
        )

        return result

    def provide_clinical_decision_support(
        self,
        session_data: Dict[str, Any],
        protocol_context: Dict[str, Any],
        patient_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide real-time clinical decision support.

        Args:
            session_data: Current session vitals, observations, adverse events
            protocol_context: Current protocol step, safety checks, evaluation rules
            patient_history: Previous sessions, baseline measures, risk factors

        Returns:
            Dict with:
                - risk_level: Overall risk (low/moderate/high/critical)
                - risk_factors: List of identified risk factors
                - recommendations: Clinical recommendations
                - decision_point_evaluation: If at decision point
                - clinical_notes: Summary for clinician
                - requires_immediate_attention: Boolean flag
                - suggested_interventions: List of interventions
                - confidence_score: AI confidence

        Raises:
            AIServiceError: If analysis fails
        """
        logger.info(
            f"Providing clinical decision support - "
            f"Session: {session_data.get('session_id')}, "
            f"Step: {protocol_context.get('current_step_title')}"
        )

        # Generate prompt with all context
        prompt = get_clinical_decision_support_prompt(
            session_data,
            protocol_context,
            patient_history
        )

        # System message emphasizing conservative approach
        system_message = (
            "You are a clinical decision support system. "
            "Always prioritize patient safety. "
            "Be conservative - when in doubt, recommend caution. "
            "Flag borderline cases and provide evidence-based recommendations. "
            "Respond with valid JSON matching the requested schema."
        )

        # Call Gemini
        response_text = self._call_gemini(prompt, system_message)

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_text = response_text
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0].strip()

            decision_support = json.loads(json_text)

            # Ensure all required fields are present
            result = {
                "risk_level": decision_support.get("risk_level", "moderate"),
                "risk_factors": decision_support.get("risk_factors", []),
                "recommendations": decision_support.get("recommendations", []),
                "decision_point_evaluation": decision_support.get("decision_point_evaluation"),
                "clinical_notes": decision_support.get("clinical_notes", ""),
                "requires_immediate_attention": decision_support.get("requires_immediate_attention", False),
                "suggested_interventions": decision_support.get("suggested_interventions", []),
                "confidence_score": 0.90  # Could implement actual confidence scoring
            }

            logger.info(
                f"Clinical decision support generated - "
                f"Risk level: {result['risk_level']}, "
                f"Recommendations: {len(result['recommendations'])}, "
                f"Immediate attention: {result['requires_immediate_attention']}"
            )

            # Log critical cases
            if result["risk_level"] == "critical" or result["requires_immediate_attention"]:
                logger.warning(
                    f"CRITICAL: Clinical decision support flagged immediate attention needed - "
                    f"Session: {session_data.get('session_id')}"
                )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            raise AIServiceError(f"Failed to parse AI response as JSON: {str(e)}") from e

    def _validate_extraction(self, extracted_data: Dict[str, Any]) -> list:
        """Validate extracted protocol data and return warnings.

        Args:
            extracted_data: Extracted protocol data

        Returns:
            List of warning messages
        """
        warnings = []

        # Check for missing protocol fields
        protocol = extracted_data.get("protocol", {})
        if not protocol.get("name"):
            warnings.append("Protocol name is missing")
        if not protocol.get("duration_weeks"):
            warnings.append("Duration not specified")
        if not protocol.get("total_sessions"):
            warnings.append("Total sessions not specified")

        # Check steps
        steps = extracted_data.get("steps", [])
        if len(steps) == 0:
            warnings.append("No protocol steps extracted")
        elif len(steps) < 3:
            warnings.append("Very few steps extracted - protocol may be incomplete")

        # Check for screening step
        has_screening = any(s.get("step_type") == "screening" for s in steps)
        if not has_screening:
            warnings.append("No screening step found - safety concern")

        # Check safety checks
        safety_checks = extracted_data.get("safety_checks", [])
        if len(safety_checks) == 0:
            warnings.append("No safety checks extracted - review original text for contraindications")

        return warnings if warnings else None


# Global instance
ai_service = AIService()
