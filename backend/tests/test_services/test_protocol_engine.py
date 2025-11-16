"""Tests for protocol engine service."""

import pytest
from app.services.protocol_engine import ProtocolEngine
from app.models.protocol import ProtocolStep, StepType


class TestFactorEvaluation:
    """Test individual factor evaluation."""

    def test_evaluate_factor_in_range(self):
        """Test in_range operator evaluation."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.weight_kg",
            "operator": "in_range",
            "ranges": [
                {"min": 0, "max": 60, "value": "low_weight"},
                {"min": 60, "max": 90, "value": "medium_weight"},
                {"min": 90, "max": 999, "value": "high_weight"}
            ]
        }

        patient_data = {"patient": {"weight_kg": 55}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "low_weight"

        patient_data = {"patient": {"weight_kg": 75}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "medium_weight"

        patient_data = {"patient": {"weight_kg": 95}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "high_weight"

    def test_evaluate_factor_threshold(self):
        """Test threshold operator evaluation."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.anxiety_score_gad7",
            "operator": "threshold",
            "thresholds": [
                {"max": 10, "value": "low_anxiety"},
                {"min": 10, "max": 15, "value": "moderate_anxiety"},
                {"min": 15, "value": "high_anxiety"}
            ]
        }

        patient_data = {"patient": {"anxiety_score_gad7": 5}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "low_anxiety"

        patient_data = {"patient": {"anxiety_score_gad7": 12}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "moderate_anxiety"

        patient_data = {"patient": {"anxiety_score_gad7": 18}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "high_anxiety"

    def test_evaluate_factor_equals(self):
        """Test equals operator evaluation."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.previous_experience",
            "operator": "equals",
            "conditions": [
                {"value": "none", "result": "naive"},
                {"value": "some", "result": "experienced"},
                {"value": "extensive", "result": "veteran"}
            ]
        }

        patient_data = {"patient": {"previous_experience": "none"}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "naive"

        patient_data = {"patient": {"previous_experience": "extensive"}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "veteran"

    def test_evaluate_factor_boolean(self):
        """Test boolean operator evaluation."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.on_medication",
            "operator": "boolean",
            "true_value": "medicated",
            "false_value": "unmedicated"
        }

        patient_data = {"patient": {"on_medication": True}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "medicated"

        patient_data = {"patient": {"on_medication": False}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "unmedicated"

    def test_evaluate_factor_missing_data(self):
        """Test factor evaluation with missing data."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.weight_kg",
            "operator": "in_range",
            "ranges": [
                {"min": 0, "max": 60, "value": "low_weight"}
            ]
        }

        patient_data = {}

        with pytest.raises(ValueError, match="Missing data"):
            engine.evaluate_factor(factor_def, patient_data)


class TestFactorCombination:
    """Test multi-factor combination with decision matrix."""

    def test_combine_factors_simple(self):
        """Test simple factor combination."""
        engine = ProtocolEngine()

        factors = ["low_weight", "high_anxiety"]
        decision_matrix = {
            "low_weight + high_anxiety": "dosage_15mg",
            "low_weight + moderate_anxiety": "dosage_20mg",
            "medium_weight + high_anxiety": "dosage_20mg",
            "medium_weight + moderate_anxiety": "dosage_25mg"
        }

        result = engine.combine_factors(factors, decision_matrix)
        assert result == "dosage_15mg"

    def test_combine_factors_three_factors(self):
        """Test combination with three factors."""
        engine = ProtocolEngine()

        factors = ["low_weight", "high_anxiety", "naive"]
        decision_matrix = {
            "low_weight + high_anxiety + naive": "dosage_10mg",
            "low_weight + high_anxiety + experienced": "dosage_15mg",
            "medium_weight + moderate_anxiety + naive": "dosage_20mg"
        }

        result = engine.combine_factors(factors, decision_matrix)
        assert result == "dosage_10mg"

    def test_combine_factors_no_match(self):
        """Test combination with no matching matrix entry."""
        engine = ProtocolEngine()

        factors = ["high_weight", "low_anxiety"]
        decision_matrix = {
            "low_weight + high_anxiety": "dosage_15mg",
            "medium_weight + moderate_anxiety": "dosage_25mg"
        }

        with pytest.raises(ValueError, match="No matching decision matrix entry"):
            engine.combine_factors(factors, decision_matrix)

    def test_combine_factors_default_fallback(self):
        """Test combination with default fallback."""
        engine = ProtocolEngine()

        factors = ["high_weight", "low_anxiety"]
        decision_matrix = {
            "low_weight + high_anxiety": "dosage_15mg",
            "medium_weight + moderate_anxiety": "dosage_25mg",
            "default": "dosage_25mg"
        }

        result = engine.combine_factors(factors, decision_matrix)
        assert result == "dosage_25mg"


class TestDecisionPointEvaluation:
    """Test complete decision point evaluation."""

    def test_evaluate_decision_point_multi_factor(self):
        """Test multi-factor decision point evaluation."""
        engine = ProtocolEngine()

        # Create a decision step
        step = ProtocolStep(
            id=1,
            protocol_id=1,
            sequence_order=5,
            step_type=StepType.DECISION_POINT,
            title="Determine Psilocybin Dosage",
            evaluation_rules={
                "type": "multi_factor",
                "factors": [
                    {
                        "factor": "patient.weight_kg",
                        "operator": "in_range",
                        "ranges": [
                            {"min": 0, "max": 60, "value": "low_weight"},
                            {"min": 60, "max": 90, "value": "medium_weight"},
                            {"min": 90, "max": 999, "value": "high_weight"}
                        ]
                    },
                    {
                        "factor": "patient.anxiety_score_gad7",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 10, "value": "low_anxiety"},
                            {"min": 10, "max": 15, "value": "moderate_anxiety"},
                            {"min": 15, "value": "high_anxiety"}
                        ]
                    }
                ],
                "decision_matrix": {
                    "low_weight + high_anxiety": "dosage_15mg",
                    "low_weight + moderate_anxiety": "dosage_20mg",
                    "medium_weight + high_anxiety": "dosage_20mg",
                    "medium_weight + moderate_anxiety": "dosage_25mg",
                    "high_weight + low_anxiety": "dosage_30mg",
                    "default": "dosage_25mg"
                }
            },
            branch_outcomes=[
                {
                    "outcome_id": "dosage_15mg",
                    "next_step_id": "step_6a",
                    "rationale": "Lower dose recommended"
                },
                {
                    "outcome_id": "dosage_20mg",
                    "next_step_id": "step_6b",
                    "rationale": "Standard lower dose"
                },
                {
                    "outcome_id": "dosage_25mg",
                    "next_step_id": "step_6c",
                    "rationale": "Standard dose"
                }
            ]
        )

        patient_data = {
            "patient": {
                "weight_kg": 55,
                "anxiety_score_gad7": 18
            }
        }

        result = engine.evaluate_decision_point(step, patient_data)
        assert result == "dosage_15mg"

    def test_evaluate_decision_point_single_factor(self):
        """Test single-factor decision point evaluation."""
        engine = ProtocolEngine()

        step = ProtocolStep(
            id=2,
            protocol_id=1,
            sequence_order=10,
            step_type=StepType.DECISION_POINT,
            title="Determine Session Continuation",
            evaluation_rules={
                "type": "single_factor",
                "factor": {
                    "factor": "patient.phq9_score",
                    "operator": "threshold",
                    "thresholds": [
                        {"max": 5, "value": "continue_treatment"},
                        {"min": 5, "value": "add_sessions"}
                    ]
                }
            },
            branch_outcomes=[
                {
                    "outcome_id": "continue_treatment",
                    "next_step_id": "step_11",
                    "rationale": "Patient showing improvement"
                },
                {
                    "outcome_id": "add_sessions",
                    "next_step_id": "step_12",
                    "rationale": "Additional sessions recommended"
                }
            ]
        )

        patient_data = {
            "patient": {
                "phq9_score": 3
            }
        }

        result = engine.evaluate_decision_point(step, patient_data)
        assert result == "continue_treatment"

    def test_evaluate_decision_point_invalid_rules(self):
        """Test decision point with invalid evaluation rules."""
        engine = ProtocolEngine()

        step = ProtocolStep(
            id=3,
            protocol_id=1,
            sequence_order=5,
            step_type=StepType.DECISION_POINT,
            title="Invalid Step",
            evaluation_rules=None
        )

        patient_data = {"patient": {"weight_kg": 75}}

        with pytest.raises(ValueError, match="Missing evaluation rules"):
            engine.evaluate_decision_point(step, patient_data)

    def test_evaluate_decision_point_complex_scenario(self):
        """Test complex decision scenario with multiple factors."""
        engine = ProtocolEngine()

        # Dose adjustment based on weight, anxiety, previous experience, and medication status
        step = ProtocolStep(
            id=4,
            protocol_id=1,
            sequence_order=5,
            step_type=StepType.DECISION_POINT,
            title="Complex Dose Determination",
            evaluation_rules={
                "type": "multi_factor",
                "factors": [
                    {
                        "factor": "patient.weight_kg",
                        "operator": "in_range",
                        "ranges": [
                            {"min": 0, "max": 70, "value": "light"},
                            {"min": 70, "max": 999, "value": "heavy"}
                        ]
                    },
                    {
                        "factor": "patient.previous_sessions",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 1, "value": "naive"},
                            {"min": 1, "value": "experienced"}
                        ]
                    },
                    {
                        "factor": "patient.on_ssri",
                        "operator": "boolean",
                        "true_value": "medicated",
                        "false_value": "unmedicated"
                    }
                ],
                "decision_matrix": {
                    "light + naive + unmedicated": "dose_20mg",
                    "light + naive + medicated": "dose_15mg",
                    "light + experienced + unmedicated": "dose_25mg",
                    "heavy + naive + unmedicated": "dose_25mg",
                    "heavy + experienced + unmedicated": "dose_30mg",
                    "heavy + experienced + medicated": "dose_25mg",
                    "default": "dose_20mg"
                }
            },
            branch_outcomes=[]
        )

        patient_data = {
            "patient": {
                "weight_kg": 65,
                "previous_sessions": 0,
                "on_ssri": True
            }
        }

        result = engine.evaluate_decision_point(step, patient_data)
        assert result == "dose_15mg"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_nested_patient_data_access(self):
        """Test accessing nested patient data."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.medical_history.cardiovascular.systolic_bp",
            "operator": "threshold",
            "thresholds": [
                {"max": 120, "value": "normal"},
                {"min": 120, "max": 140, "value": "elevated"},
                {"min": 140, "value": "high"}
            ]
        }

        patient_data = {
            "patient": {
                "medical_history": {
                    "cardiovascular": {
                        "systolic_bp": 135
                    }
                }
            }
        }

        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "elevated"

    def test_boundary_values_in_range(self):
        """Test boundary values in range operator."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.age",
            "operator": "in_range",
            "ranges": [
                {"min": 18, "max": 30, "value": "young"},
                {"min": 30, "max": 50, "value": "middle"},
                {"min": 50, "max": 100, "value": "senior"}
            ]
        }

        # Test exact boundary at 30
        patient_data = {"patient": {"age": 30}}
        result = engine.evaluate_factor(factor_def, patient_data)
        assert result == "middle"  # Should match the second range (min inclusive)

    def test_invalid_operator(self):
        """Test invalid operator in factor definition."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.weight_kg",
            "operator": "invalid_operator",
            "ranges": []
        }

        patient_data = {"patient": {"weight_kg": 75}}

        with pytest.raises(ValueError, match="Unknown operator"):
            engine.evaluate_factor(factor_def, patient_data)

    def test_missing_threshold_definition(self):
        """Test threshold operator without thresholds defined."""
        engine = ProtocolEngine()

        factor_def = {
            "factor": "patient.score",
            "operator": "threshold"
            # Missing "thresholds" key
        }

        patient_data = {"patient": {"score": 10}}

        with pytest.raises(ValueError, match="Missing thresholds"):
            engine.evaluate_factor(factor_def, patient_data)
