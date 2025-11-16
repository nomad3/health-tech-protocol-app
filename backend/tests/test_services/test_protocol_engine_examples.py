"""
Example decision scenarios demonstrating the Protocol Engine.

These examples show real-world use cases for decision point evaluation
in psychedelic therapy protocols.
"""

import pytest
from app.services.protocol_engine import ProtocolEngine
from app.models.protocol import ProtocolStep, StepType


class TestRealWorldScenarios:
    """Test realistic clinical decision scenarios."""

    def test_psilocybin_dose_determination(self):
        """
        Example: Psilocybin dose determination based on multiple factors.

        This scenario evaluates:
        - Patient body weight
        - Anxiety level (GAD-7 score)
        - Previous psychedelic experience
        """
        engine = ProtocolEngine()

        step = ProtocolStep(
            id=1,
            protocol_id=1,
            sequence_order=5,
            step_type=StepType.DECISION_POINT,
            title="Psilocybin Dose Determination",
            description="Determine appropriate psilocybin dose based on patient factors",
            evaluation_rules={
                "type": "multi_factor",
                "factors": [
                    {
                        "factor": "patient.weight_kg",
                        "operator": "in_range",
                        "ranges": [
                            {"min": 0, "max": 60, "value": "low_weight"},
                            {"min": 60, "max": 85, "value": "medium_weight"},
                            {"min": 85, "max": 999, "value": "high_weight"},
                        ],
                    },
                    {
                        "factor": "patient.anxiety_score_gad7",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 10, "value": "low_anxiety"},
                            {"min": 10, "max": 15, "value": "moderate_anxiety"},
                            {"min": 15, "value": "high_anxiety"},
                        ],
                    },
                    {
                        "factor": "patient.previous_psychedelic_sessions",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 1, "value": "naive"},
                            {"min": 1, "value": "experienced"},
                        ],
                    },
                ],
                "decision_matrix": {
                    "low_weight + high_anxiety + naive": "15mg",
                    "low_weight + moderate_anxiety + naive": "20mg",
                    "low_weight + low_anxiety + naive": "20mg",
                    "medium_weight + high_anxiety + naive": "20mg",
                    "medium_weight + moderate_anxiety + naive": "25mg",
                    "medium_weight + low_anxiety + naive": "25mg",
                    "high_weight + high_anxiety + naive": "25mg",
                    "high_weight + moderate_anxiety + naive": "30mg",
                    "high_weight + low_anxiety + naive": "30mg",
                    "low_weight + high_anxiety + experienced": "20mg",
                    "medium_weight + moderate_anxiety + experienced": "30mg",
                    "high_weight + low_anxiety + experienced": "35mg",
                    "default": "25mg",  # Standard dose
                },
            },
            branch_outcomes=[
                {
                    "outcome_id": "15mg",
                    "next_step_id": "dosing_15mg",
                    "rationale": "Conservative dose for low weight and high anxiety",
                },
                {
                    "outcome_id": "25mg",
                    "next_step_id": "dosing_25mg",
                    "rationale": "Standard dose",
                },
                {
                    "outcome_id": "35mg",
                    "next_step_id": "dosing_35mg",
                    "rationale": "Higher dose for experienced patient with high tolerance",
                },
            ],
        )

        # Test Case 1: First-time patient, low weight, high anxiety
        patient_1 = {
            "patient": {
                "weight_kg": 55,
                "anxiety_score_gad7": 17,
                "previous_psychedelic_sessions": 0,
            }
        }
        result = engine.evaluate_decision_point(step, patient_1)
        assert result == "15mg"
        print(f"Patient 1 (55kg, GAD-7: 17, naive): {result}")

        # Test Case 2: Standard patient
        patient_2 = {
            "patient": {
                "weight_kg": 70,
                "anxiety_score_gad7": 12,
                "previous_psychedelic_sessions": 0,
            }
        }
        result = engine.evaluate_decision_point(step, patient_2)
        assert result == "25mg"
        print(f"Patient 2 (70kg, GAD-7: 12, naive): {result}")

        # Test Case 3: Experienced patient, high weight, low anxiety
        patient_3 = {
            "patient": {
                "weight_kg": 90,
                "anxiety_score_gad7": 5,
                "previous_psychedelic_sessions": 3,
            }
        }
        result = engine.evaluate_decision_point(step, patient_3)
        assert result == "35mg"
        print(f"Patient 3 (90kg, GAD-7: 5, experienced): {result}")

    def test_mdma_session_continuation_decision(self):
        """
        Example: MDMA protocol - decide if additional sessions are needed.

        Evaluates treatment response after initial MDMA sessions.
        """
        engine = ProtocolEngine()

        step = ProtocolStep(
            id=2,
            protocol_id=2,
            sequence_order=12,
            step_type=StepType.DECISION_POINT,
            title="Evaluate Treatment Response",
            description="Determine if additional MDMA sessions are warranted",
            evaluation_rules={
                "type": "multi_factor",
                "factors": [
                    {
                        "factor": "patient.caps5_score",  # PTSD assessment
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 20, "value": "significant_improvement"},
                            {
                                "min": 20,
                                "max": 40,
                                "value": "moderate_improvement",
                            },
                            {"min": 40, "value": "minimal_improvement"},
                        ],
                    },
                    {
                        "factor": "patient.sessions_completed",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 3, "value": "early_treatment"},
                            {"min": 3, "value": "extended_treatment"},
                        ],
                    },
                ],
                "decision_matrix": {
                    "significant_improvement + early_treatment": "complete_protocol",
                    "significant_improvement + extended_treatment": "complete_protocol",
                    "moderate_improvement + early_treatment": "add_one_session",
                    "moderate_improvement + extended_treatment": "complete_protocol",
                    "minimal_improvement + early_treatment": "add_two_sessions",
                    "minimal_improvement + extended_treatment": "refer_specialist",
                },
            },
        )

        # Test Case 1: Good response after 2 sessions
        patient_1 = {"patient": {"caps5_score": 18, "sessions_completed": 2}}
        result = engine.evaluate_decision_point(step, patient_1)
        assert result == "complete_protocol"
        print(f"Patient 1 (CAPS-5: 18, 2 sessions): {result}")

        # Test Case 2: Moderate response, needs one more session
        patient_2 = {"patient": {"caps5_score": 25, "sessions_completed": 2}}
        result = engine.evaluate_decision_point(step, patient_2)
        assert result == "add_one_session"
        print(f"Patient 2 (CAPS-5: 25, 2 sessions): {result}")

        # Test Case 3: Minimal response after extended treatment
        patient_3 = {"patient": {"caps5_score": 45, "sessions_completed": 4}}
        result = engine.evaluate_decision_point(step, patient_3)
        assert result == "refer_specialist"
        print(f"Patient 3 (CAPS-5: 45, 4 sessions): {result}")

    def test_ketamine_cardiovascular_safety_check(self):
        """
        Example: Ketamine infusion - cardiovascular safety decision.

        Ketamine can increase blood pressure, so we need to evaluate
        cardiovascular risk before proceeding.
        """
        engine = ProtocolEngine()

        step = ProtocolStep(
            id=3,
            protocol_id=3,
            sequence_order=2,
            step_type=StepType.DECISION_POINT,
            title="Cardiovascular Safety Evaluation",
            description="Assess cardiovascular safety for ketamine infusion",
            evaluation_rules={
                "type": "multi_factor",
                "factors": [
                    {
                        "factor": "patient.baseline_systolic_bp",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 130, "value": "normal_bp"},
                            {"min": 130, "max": 150, "value": "elevated_bp"},
                            {"min": 150, "value": "high_bp"},
                        ],
                    },
                    {
                        "factor": "patient.cardiovascular_history",
                        "operator": "boolean",
                        "true_value": "cv_history",
                        "false_value": "no_cv_history",
                    },
                    {
                        "factor": "patient.age",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 50, "value": "under_50"},
                            {"min": 50, "value": "over_50"},
                        ],
                    },
                ],
                "decision_matrix": {
                    "normal_bp + no_cv_history + under_50": "proceed_standard",
                    "normal_bp + no_cv_history + over_50": "proceed_standard",
                    "elevated_bp + no_cv_history + under_50": "proceed_monitoring",
                    "elevated_bp + no_cv_history + over_50": "proceed_monitoring",
                    "elevated_bp + cv_history + under_50": "cardiology_clearance",
                    "elevated_bp + cv_history + over_50": "cardiology_clearance",
                    "high_bp + no_cv_history + under_50": "cardiology_clearance",
                    "high_bp + cv_history + under_50": "contraindicated",
                    "high_bp + cv_history + over_50": "contraindicated",
                    "default": "cardiology_clearance",
                },
            },
        )

        # Test Case 1: Healthy young patient
        patient_1 = {
            "patient": {
                "baseline_systolic_bp": 120,
                "cardiovascular_history": False,
                "age": 35,
            }
        }
        result = engine.evaluate_decision_point(step, patient_1)
        assert result == "proceed_standard"
        print(f"Patient 1 (BP: 120, no CV history, age 35): {result}")

        # Test Case 2: Elevated BP, no history, older patient
        patient_2 = {
            "patient": {
                "baseline_systolic_bp": 140,
                "cardiovascular_history": False,
                "age": 55,
            }
        }
        result = engine.evaluate_decision_point(step, patient_2)
        assert result == "proceed_monitoring"
        print(f"Patient 2 (BP: 140, no CV history, age 55): {result}")

        # Test Case 3: High BP with CV history - contraindicated
        patient_3 = {
            "patient": {
                "baseline_systolic_bp": 160,
                "cardiovascular_history": True,
                "age": 60,
            }
        }
        result = engine.evaluate_decision_point(step, patient_3)
        assert result == "contraindicated"
        print(f"Patient 3 (BP: 160, CV history, age 60): {result}")

    def test_integration_session_frequency_decision(self):
        """
        Example: Determine integration session frequency based on patient needs.
        """
        engine = ProtocolEngine()

        step = ProtocolStep(
            id=4,
            protocol_id=1,
            sequence_order=8,
            step_type=StepType.DECISION_POINT,
            title="Integration Session Frequency",
            description="Determine optimal frequency for integration sessions",
            evaluation_rules={
                "type": "multi_factor",
                "factors": [
                    {
                        "factor": "patient.integration_needs_score",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 5, "value": "low_needs"},
                            {"min": 5, "max": 8, "value": "moderate_needs"},
                            {"min": 8, "value": "high_needs"},
                        ],
                    },
                    {
                        "factor": "patient.support_system",
                        "operator": "equals",
                        "conditions": [
                            {"value": "strong", "result": "strong_support"},
                            {"value": "moderate", "result": "moderate_support"},
                            {"value": "limited", "result": "limited_support"},
                        ],
                    },
                ],
                "decision_matrix": {
                    "low_needs + strong_support": "biweekly",
                    "low_needs + moderate_support": "weekly",
                    "moderate_needs + strong_support": "weekly",
                    "moderate_needs + moderate_support": "weekly",
                    "moderate_needs + limited_support": "twice_weekly",
                    "high_needs + strong_support": "weekly",
                    "high_needs + moderate_support": "twice_weekly",
                    "high_needs + limited_support": "twice_weekly",
                },
            },
        )

        # Test Case 1: Low needs, strong support
        patient_1 = {
            "patient": {"integration_needs_score": 3, "support_system": "strong"}
        }
        result = engine.evaluate_decision_point(step, patient_1)
        assert result == "biweekly"
        print(f"Patient 1 (needs: 3, strong support): {result}")

        # Test Case 2: High needs, limited support
        patient_2 = {
            "patient": {"integration_needs_score": 9, "support_system": "limited"}
        }
        result = engine.evaluate_decision_point(step, patient_2)
        assert result == "twice_weekly"
        print(f"Patient 2 (needs: 9, limited support): {result}")

    def test_nested_medical_data_evaluation(self):
        """
        Example: Complex nested medical data evaluation.

        Demonstrates deep nested data access from electronic health records.
        """
        engine = ProtocolEngine()

        step = ProtocolStep(
            id=5,
            protocol_id=1,
            sequence_order=3,
            step_type=StepType.DECISION_POINT,
            title="Liver Function Assessment",
            description="Evaluate liver function for medication metabolism",
            evaluation_rules={
                "type": "multi_factor",
                "factors": [
                    {
                        "factor": "patient.labs.liver_function.alt",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 40, "value": "normal_alt"},
                            {"min": 40, "max": 80, "value": "elevated_alt"},
                            {"min": 80, "value": "high_alt"},
                        ],
                    },
                    {
                        "factor": "patient.labs.liver_function.ast",
                        "operator": "threshold",
                        "thresholds": [
                            {"max": 40, "value": "normal_ast"},
                            {"min": 40, "max": 80, "value": "elevated_ast"},
                            {"min": 80, "value": "high_ast"},
                        ],
                    },
                ],
                "decision_matrix": {
                    "normal_alt + normal_ast": "proceed",
                    "normal_alt + elevated_ast": "proceed_monitoring",
                    "elevated_alt + normal_ast": "proceed_monitoring",
                    "elevated_alt + elevated_ast": "hepatology_consult",
                    "high_alt + normal_ast": "hepatology_consult",
                    "normal_alt + high_ast": "hepatology_consult",
                    "default": "hepatology_consult",
                },
            },
        )

        # Test Case: Normal liver function
        patient = {
            "patient": {
                "labs": {"liver_function": {"alt": 25, "ast": 30}},
                "demographics": {"age": 45},
            }
        }

        result = engine.evaluate_decision_point(step, patient)
        assert result == "proceed"
        print(f"Patient (ALT: 25, AST: 30): {result}")


class TestExampleOutputs:
    """Generate example outputs for documentation."""

    def test_print_example_decision_evaluations(self):
        """
        Print example decision evaluations for documentation.
        """
        engine = ProtocolEngine()

        print("\n" + "=" * 70)
        print("PROTOCOL ENGINE - EXAMPLE DECISION EVALUATIONS")
        print("=" * 70)

        # Example 1: Simple dose calculation
        print("\nExample 1: Psilocybin Dose Determination")
        print("-" * 70)

        patient = {"patient": {"weight_kg": 65, "anxiety_score_gad7": 8}}

        print(f"Patient Data: {patient}")
        print("\nFactor Evaluations:")

        # Evaluate individual factors
        weight_factor = {
            "factor": "patient.weight_kg",
            "operator": "in_range",
            "ranges": [
                {"min": 0, "max": 60, "value": "low_weight"},
                {"min": 60, "max": 85, "value": "medium_weight"},
                {"min": 85, "max": 999, "value": "high_weight"},
            ],
        }
        weight_result = engine.evaluate_factor(weight_factor, patient)
        print(f"  - Weight (65kg) → {weight_result}")

        anxiety_factor = {
            "factor": "patient.anxiety_score_gad7",
            "operator": "threshold",
            "thresholds": [
                {"max": 10, "value": "low_anxiety"},
                {"min": 10, "max": 15, "value": "moderate_anxiety"},
                {"min": 15, "value": "high_anxiety"},
            ],
        }
        anxiety_result = engine.evaluate_factor(anxiety_factor, patient)
        print(f"  - Anxiety (GAD-7: 8) → {anxiety_result}")

        decision_matrix = {
            "medium_weight + low_anxiety": "dosage_25mg",
            "medium_weight + moderate_anxiety": "dosage_25mg",
        }

        final_result = engine.combine_factors(
            [weight_result, anxiety_result], decision_matrix
        )
        print(f"\nFinal Decision: {final_result}")

        # Example 2: Safety evaluation
        print("\n\nExample 2: Cardiovascular Safety Check")
        print("-" * 70)

        patient = {
            "patient": {
                "baseline_systolic_bp": 145,
                "cardiovascular_history": False,
                "age": 52,
            }
        }

        print(f"Patient Data: {patient}")
        print("\nSafety Evaluation:")
        print(f"  - Blood Pressure: 145 (elevated)")
        print(f"  - CV History: None")
        print(f"  - Age: 52")
        print(f"\nDecision: proceed_monitoring")
        print(
            "  Rationale: Proceed with enhanced cardiovascular monitoring during infusion"
        )

        print("\n" + "=" * 70 + "\n")
