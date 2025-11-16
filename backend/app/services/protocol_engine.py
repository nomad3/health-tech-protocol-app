"""Protocol engine service for decision point evaluation."""

from typing import Any, Dict, List, Optional
from app.models.protocol import ProtocolStep


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
