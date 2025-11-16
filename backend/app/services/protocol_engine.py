"""Protocol engine service for decision point evaluation and protocol execution."""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.protocol import Protocol, ProtocolStep, StepType
from app.models.treatment import TreatmentPlan, TreatmentSession, SessionStatus, TreatmentStatus
from app.services.safety_service import SafetyService


class ProtocolEngine:
    """
    Protocol engine for evaluating decision points and determining treatment paths.

    This engine supports multi-factor evaluation with decision matrices,
    enabling dynamic protocol branching based on patient data.
    """

    def evaluate_decision_point(
        self, decision_step: ProtocolStep, patient_data: dict
    ) -> str:
        """
        Evaluate a decision point and return the outcome_id for the next step.

        Args:
            decision_step: ProtocolStep with evaluation_rules and branch_outcomes
            patient_data: Dictionary containing patient data for evaluation

        Returns:
            outcome_id: The ID of the outcome/branch to take

        Raises:
            ValueError: If evaluation rules are missing or invalid
        """
        if not decision_step.evaluation_rules:
            raise ValueError("Missing evaluation rules for decision point")

        rules = decision_step.evaluation_rules
        rule_type = rules.get("type")

        if rule_type == "single_factor":
            # Single factor evaluation
            factor_def = rules.get("factor")
            if not factor_def:
                raise ValueError("Missing factor definition for single_factor type")
            return self.evaluate_factor(factor_def, patient_data)

        elif rule_type == "multi_factor":
            # Multi-factor evaluation with decision matrix
            factors_def = rules.get("factors")
            decision_matrix = rules.get("decision_matrix")

            if not factors_def or not decision_matrix:
                raise ValueError(
                    "Missing factors or decision_matrix for multi_factor type"
                )

            # Evaluate each factor
            factor_results = []
            for factor_def in factors_def:
                result = self.evaluate_factor(factor_def, patient_data)
                factor_results.append(result)

            # Combine factors using decision matrix
            return self.combine_factors(factor_results, decision_matrix)

        else:
            raise ValueError(f"Unknown evaluation rule type: {rule_type}")

    def evaluate_factor(self, factor_def: dict, patient_data: dict) -> str:
        """
        Evaluate a single factor against patient data.

        Supports operators:
        - in_range: Check if value falls within specified ranges
        - threshold: Check if value crosses specified thresholds
        - equals: Check for exact value matches
        - boolean: Evaluate boolean conditions

        Args:
            factor_def: Factor definition with operator and conditions
            patient_data: Dictionary containing patient data

        Returns:
            String value representing the evaluation result

        Raises:
            ValueError: If factor data is missing or operator is unknown
        """
        factor_path = factor_def.get("factor")
        operator = factor_def.get("operator")

        if not factor_path or not operator:
            raise ValueError("Factor definition must include 'factor' and 'operator'")

        # Extract value from nested patient data
        value = self._get_nested_value(patient_data, factor_path)

        if value is None:
            raise ValueError(f"Missing data for factor: {factor_path}")

        # Evaluate based on operator
        if operator == "in_range":
            return self._evaluate_in_range(value, factor_def.get("ranges", []))

        elif operator == "threshold":
            thresholds = factor_def.get("thresholds")
            if not thresholds:
                raise ValueError("Missing thresholds for threshold operator")
            return self._evaluate_threshold(value, thresholds)

        elif operator == "equals":
            return self._evaluate_equals(value, factor_def.get("conditions", []))

        elif operator == "boolean":
            return self._evaluate_boolean(
                value, factor_def.get("true_value"), factor_def.get("false_value")
            )

        else:
            raise ValueError(f"Unknown operator: {operator}")

    def combine_factors(self, factors: List[str], decision_matrix: dict) -> str:
        """
        Combine multiple factor results using a decision matrix.

        Args:
            factors: List of factor evaluation results
            decision_matrix: Dictionary mapping factor combinations to outcomes

        Returns:
            outcome_id from the decision matrix

        Raises:
            ValueError: If no matching matrix entry is found
        """
        # Create key by joining factors with " + "
        matrix_key = " + ".join(factors)

        # Look for exact match
        if matrix_key in decision_matrix:
            return decision_matrix[matrix_key]

        # Look for default fallback
        if "default" in decision_matrix:
            return decision_matrix["default"]

        # No match found
        raise ValueError(
            f"No matching decision matrix entry for: {matrix_key}. "
            f"Available entries: {list(decision_matrix.keys())}"
        )

    def _get_nested_value(self, data: dict, path: str) -> Any:
        """
        Extract value from nested dictionary using dot notation.

        Args:
            data: Dictionary to extract from
            path: Dot-separated path (e.g., "patient.weight_kg")

        Returns:
            Value at the specified path, or None if not found
        """
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def _evaluate_in_range(self, value: float, ranges: List[dict]) -> str:
        """
        Evaluate if value falls within specified ranges.

        Args:
            value: Numeric value to check
            ranges: List of range definitions with min, max, and value

        Returns:
            Value string from matching range

        Raises:
            ValueError: If value doesn't match any range
        """
        for range_def in ranges:
            min_val = range_def.get("min", float("-inf"))
            max_val = range_def.get("max", float("inf"))

            # Check if value is in range (min inclusive, max exclusive)
            # Except for the last range where max is also inclusive
            if min_val <= value < max_val or (
                value == max_val and range_def == ranges[-1]
            ):
                return range_def.get("value")

        raise ValueError(f"Value {value} does not match any range")

    def _evaluate_threshold(self, value: float, thresholds: List[dict]) -> str:
        """
        Evaluate value against thresholds.

        Args:
            value: Numeric value to check
            thresholds: List of threshold definitions

        Returns:
            Value string from matching threshold

        Raises:
            ValueError: If value doesn't match any threshold
        """
        for threshold in thresholds:
            min_val = threshold.get("min", float("-inf"))
            max_val = threshold.get("max", float("inf"))

            if min_val <= value < max_val or (
                value == max_val and threshold == thresholds[-1]
            ):
                return threshold.get("value")

        raise ValueError(f"Value {value} does not match any threshold")

    def _evaluate_equals(self, value: Any, conditions: List[dict]) -> str:
        """
        Evaluate exact value matches.

        Args:
            value: Value to check
            conditions: List of condition definitions with value and result

        Returns:
            Result string from matching condition

        Raises:
            ValueError: If no condition matches
        """
        for condition in conditions:
            if value == condition.get("value"):
                return condition.get("result")

        raise ValueError(f"Value {value} does not match any condition")

    def _evaluate_boolean(
        self, value: bool, true_value: Optional[str], false_value: Optional[str]
    ) -> str:
        """
        Evaluate boolean conditions.

        Args:
            value: Boolean value
            true_value: String to return if True
            false_value: String to return if False

        Returns:
            true_value or false_value based on condition

        Raises:
            ValueError: If true_value or false_value not provided
        """
        if value is True:
            if true_value is None:
                raise ValueError("Missing true_value for boolean operator")
            return true_value
        else:
            if false_value is None:
                raise ValueError("Missing false_value for boolean operator")
            return false_value

    def get_current_step(self, treatment_plan: TreatmentPlan) -> Optional[ProtocolStep]:
        """
        Get the current active step for a treatment plan.

        This method determines which step the patient is currently on
        based on completed sessions and the protocol sequence.

        Args:
            treatment_plan: TreatmentPlan instance with protocol and sessions loaded

        Returns:
            Current ProtocolStep to be performed, or None if all steps are complete
        """
        # Get all completed sessions for this treatment plan
        completed_session_step_ids = set()
        for session in treatment_plan.sessions:
            if session.status == SessionStatus.COMPLETED:
                completed_session_step_ids.add(session.protocol_step_id)

        # Get all steps for the protocol, ordered by sequence
        protocol_steps = sorted(treatment_plan.protocol.steps, key=lambda s: s.sequence_order)

        # Find first step that hasn't been completed
        for step in protocol_steps:
            if step.id not in completed_session_step_ids:
                return step

        # All steps completed
        return None

    def get_next_step(
        self,
        protocol: Protocol,
        current_step: ProtocolStep,
        patient_data: Optional[dict] = None
    ) -> Optional[ProtocolStep]:
        """
        Determine the next step in the protocol.

        Handles both linear progression and decision point branches.

        Args:
            protocol: Protocol instance with steps loaded
            current_step: Current ProtocolStep
            patient_data: Patient data for decision point evaluation (required for decision points)

        Returns:
            Next ProtocolStep to perform, or None if protocol is complete

        Raises:
            ValueError: If decision point step lacks patient_data
        """
        # If current step is a decision point, evaluate it
        if current_step.step_type == StepType.DECISION_POINT:
            if patient_data is None:
                raise ValueError("patient_data required for decision point evaluation")

            # Evaluate decision point to get outcome
            outcome_id = self.evaluate_decision_point(current_step, patient_data)

            # Find the next step based on outcome
            branch_outcomes = current_step.branch_outcomes
            if not branch_outcomes:
                raise ValueError("Decision point missing branch_outcomes")

            # Find matching outcome
            next_step_order = None
            for outcome in branch_outcomes:
                if outcome.get("outcome_id") == outcome_id:
                    next_step_order = outcome.get("next_step_order")
                    break

            if next_step_order is None:
                raise ValueError(f"No branch found for outcome: {outcome_id}")

            # Find step with matching sequence order
            for step in protocol.steps:
                if step.sequence_order == next_step_order:
                    return step

            raise ValueError(f"No step found with sequence_order: {next_step_order}")

        # Linear progression - get next step in sequence
        next_order = current_step.sequence_order + 1

        for step in protocol.steps:
            if step.sequence_order == next_order:
                return step

        # No next step found - protocol complete
        return None

    def is_protocol_complete(self, treatment_plan: TreatmentPlan) -> bool:
        """
        Check if all required steps in the protocol are completed.

        Args:
            treatment_plan: TreatmentPlan instance with protocol and sessions loaded

        Returns:
            True if all protocol steps are completed, False otherwise
        """
        # Get all completed session step IDs
        completed_session_step_ids = set()
        for session in treatment_plan.sessions:
            if session.status == SessionStatus.COMPLETED:
                completed_session_step_ids.add(session.protocol_step_id)

        # Get all protocol step IDs
        protocol_step_ids = set(step.id for step in treatment_plan.protocol.steps)

        # Check if all protocol steps have been completed
        return protocol_step_ids.issubset(completed_session_step_ids)

    def can_progress_to_step(
        self,
        treatment_plan: TreatmentPlan,
        next_step: ProtocolStep,
        patient_data: dict,
        db: Session
    ) -> dict:
        """
        Validate if patient can progress to the next step.

        Runs safety checks and validates prerequisites.

        Args:
            treatment_plan: TreatmentPlan instance
            next_step: ProtocolStep to validate progression to
            patient_data: Patient data for safety evaluation
            db: Database session

        Returns:
            Dictionary with:
                - can_progress: bool - Whether progression is allowed
                - blockers: list - Blocking contraindications preventing progression
                - warnings: list - Warnings that don't block but require attention
                - risk_factors: list - Informational risk factors
        """
        # Initialize safety service
        safety_service = SafetyService()

        # Get all safety checks for this step
        safety_checks = next_step.safety_checks

        # Run safety check evaluation
        safety_result = safety_service.check_contraindications(patient_data, safety_checks)

        # Can progress only if eligible (no blocking contraindications)
        can_progress = safety_result["eligible"]

        return {
            "can_progress": can_progress,
            "blockers": safety_result["contraindications"],
            "warnings": safety_result["warnings"],
            "risk_factors": safety_result["risk_factors"]
        }
