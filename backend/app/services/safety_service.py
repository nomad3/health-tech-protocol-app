from typing import List, Dict, Any
from app.models.protocol import SafetyCheck


class SafetyService:
    """Service for evaluating safety checks and contraindications.

    This service implements a tiered safety approach:
    - Blocking contraindications (absolute): Risk score 100, patient not eligible
    - Warnings (relative contraindications): Risk score +20 each, require override
    - Risk factors (informational): Risk score +5 each, tracked but don't block
    """

    def check_contraindications(
        self,
        patient_data: dict,
        safety_checks: List[SafetyCheck]
    ) -> dict:
        """Evaluate all safety checks against patient data.

        Args:
            patient_data: Dictionary containing patient information including:
                - age: Patient age (int)
                - diagnoses: List of ICD-10 codes or condition names
                - medications: List of medication dicts with name and class
                - lab_values: Dict of lab test names to values
                - vital_signs: Dict of vital sign names to values
            safety_checks: List of SafetyCheck model instances to evaluate

        Returns:
            Dictionary containing:
                - eligible: bool - Whether patient is eligible (no blocking contraindications)
                - risk_score: int (0-100) - Overall risk score
                - contraindications: List of blocking contraindications found
                - warnings: List of relative contraindications (warnings)
                - risk_factors: List of informational risk factors
        """
        contraindications = []
        warnings = []
        risk_factors = []

        # Evaluate each safety check
        for safety_check in safety_checks:
            result = self.evaluate_safety_check(safety_check, patient_data)

            if result["triggered"]:
                item = {
                    "severity": result["severity"],
                    "message": result["message"],
                    "override_allowed": result["override_allowed"],
                    "check_type": safety_check.check_type,
                    "condition": safety_check.condition
                }

                if result["severity"] == "blocking":
                    contraindications.append(item)
                elif result["severity"] == "warning":
                    warnings.append(item)
                else:  # info
                    risk_factors.append(item)

        # Calculate overall risk score
        risk_score = self.calculate_risk_score(contraindications, warnings, risk_factors)

        # Patient is eligible only if no blocking contraindications
        eligible = len(contraindications) == 0

        return {
            "eligible": eligible,
            "risk_score": risk_score,
            "contraindications": contraindications,
            "warnings": warnings,
            "risk_factors": risk_factors
        }

    def evaluate_safety_check(
        self,
        safety_check: SafetyCheck,
        patient_data: dict
    ) -> dict:
        """Evaluate a single safety check against patient data.

        Args:
            safety_check: SafetyCheck model instance
            patient_data: Dictionary containing patient information

        Returns:
            Dictionary containing:
                - triggered: bool - Whether this check was triggered
                - severity: str - Severity level (blocking, warning, info)
                - message: str - Human-readable message about the issue
                - override_allowed: bool - Whether this can be overridden
        """
        condition = safety_check.condition
        condition_type = condition.get("type")
        triggered = False
        message = ""

        if condition_type == "diagnosis":
            triggered, message = self._check_diagnosis(condition, patient_data)
        elif condition_type == "medication":
            triggered, message = self._check_medication(condition, patient_data)
        elif condition_type == "lab_value":
            triggered, message = self._check_lab_value(condition, patient_data)
        elif condition_type == "age":
            triggered, message = self._check_age(condition, patient_data)
        elif condition_type == "vital_sign":
            triggered, message = self._check_vital_sign(condition, patient_data)
        else:
            # Unknown condition type
            triggered = False
            message = f"Unknown condition type: {condition_type}"

        return {
            "triggered": triggered,
            "severity": safety_check.severity,
            "message": message,
            "override_allowed": safety_check.override_allowed == "true"
        }

    def _check_diagnosis(self, condition: dict, patient_data: dict) -> tuple[bool, str]:
        """Check diagnosis-based condition.

        Args:
            condition: Condition definition with type, value, operator
            patient_data: Patient data including diagnoses list

        Returns:
            Tuple of (triggered: bool, message: str)
        """
        diagnoses = patient_data.get("diagnoses", [])
        value = condition.get("value")
        operator = condition.get("operator", "contains")

        if operator == "contains":
            # Check if any diagnosis contains the value (e.g., F20 matches F20.0, F20.1)
            for diagnosis in diagnoses:
                if value in diagnosis:
                    return True, f"Patient has diagnosis containing {value}: {diagnosis}"
        elif operator == "exact":
            # Check for exact match
            if value in diagnoses:
                return True, f"Patient has diagnosis {value}"

        return False, ""

    def _check_medication(self, condition: dict, patient_data: dict) -> tuple[bool, str]:
        """Check medication-based condition.

        Args:
            condition: Condition definition with type, value, operator
            patient_data: Patient data including medications list

        Returns:
            Tuple of (triggered: bool, message: str)
        """
        medications = patient_data.get("medications", [])
        value = condition.get("value")
        operator = condition.get("operator", "name_match")

        if operator == "class_match":
            # Check if any medication belongs to the specified class
            for med in medications:
                if med.get("class") == value:
                    return True, f"Patient is taking {value}: {med.get('name')}"
        elif operator == "name_match":
            # Check if any medication has the specified name
            for med in medications:
                if med.get("name") == value:
                    return True, f"Patient is taking {value}"

        return False, ""

    def _check_lab_value(self, condition: dict, patient_data: dict) -> tuple[bool, str]:
        """Check lab value-based condition.

        Args:
            condition: Condition definition with name, operator, threshold
            patient_data: Patient data including lab_values dict

        Returns:
            Tuple of (triggered: bool, message: str)
        """
        lab_values = patient_data.get("lab_values", {})
        lab_name = condition.get("name")
        operator = condition.get("operator")
        threshold = condition.get("threshold")

        if lab_name not in lab_values:
            return False, ""

        value = lab_values[lab_name]

        if operator == "greater_than":
            if value > threshold:
                return True, f"{lab_name} is {value}, above threshold of {threshold}"
        elif operator == "less_than":
            if value < threshold:
                return True, f"{lab_name} is {value}, below threshold of {threshold}"
        elif operator == "equals":
            if value == threshold:
                return True, f"{lab_name} is {value}, equals threshold of {threshold}"

        return False, ""

    def _check_age(self, condition: dict, patient_data: dict) -> tuple[bool, str]:
        """Check age-based condition.

        Args:
            condition: Condition definition with operator, threshold
            patient_data: Patient data including age

        Returns:
            Tuple of (triggered: bool, message: str)
        """
        age = patient_data.get("age")
        if age is None:
            return False, ""

        operator = condition.get("operator")
        threshold = condition.get("threshold")

        if operator == "less_than":
            if age < threshold:
                return True, f"Patient age {age} is below minimum of {threshold}"
        elif operator == "greater_than":
            if age > threshold:
                return True, f"Patient age {age} is above maximum of {threshold}"

        return False, ""

    def _check_vital_sign(self, condition: dict, patient_data: dict) -> tuple[bool, str]:
        """Check vital sign-based condition.

        Args:
            condition: Condition definition with name, operator, threshold
            patient_data: Patient data including vital_signs dict

        Returns:
            Tuple of (triggered: bool, message: str)
        """
        vital_signs = patient_data.get("vital_signs", {})
        vital_name = condition.get("name")
        operator = condition.get("operator")
        threshold = condition.get("threshold")

        if vital_name not in vital_signs:
            return False, ""

        value = vital_signs[vital_name]

        if operator == "greater_than":
            if value > threshold:
                return True, f"{vital_name} is {value}, above threshold of {threshold}"
        elif operator == "less_than":
            if value < threshold:
                return True, f"{vital_name} is {value}, below threshold of {threshold}"

        return False, ""

    def calculate_risk_score(
        self,
        contraindications: list,
        warnings: list,
        risk_factors: list
    ) -> int:
        """Calculate overall risk score based on contraindications, warnings, and risk factors.

        Scoring algorithm:
        - Any blocking contraindication: 100 (not eligible)
        - Each warning: +20 points
        - Each risk factor: +5 points
        - Maximum score: 100

        Args:
            contraindications: List of blocking contraindications
            warnings: List of warnings (relative contraindications)
            risk_factors: List of informational risk factors

        Returns:
            Risk score from 0-100
        """
        # If any blocking contraindication, return 100
        if len(contraindications) > 0:
            return 100

        # Calculate score from warnings and risk factors
        score = 0
        score += len(warnings) * 20
        score += len(risk_factors) * 5

        # Cap at 100
        return min(score, 100)

    def check_medication_interactions(
        self,
        patient_medications: list,
        therapy_type: str
    ) -> list:
        """Check for drug-drug and drug-therapy interactions.

        Args:
            patient_medications: List of patient medications with name and class
            therapy_type: Type of therapy being considered (e.g., "psilocybin", "testosterone")

        Returns:
            List of interaction dictionaries with severity, message, and recommendation
        """
        interactions = []

        # Extract medication classes for easier checking
        medication_classes = [med.get("class") for med in patient_medications if med.get("class")]
        medication_names = [med.get("name") for med in patient_medications if med.get("name")]

        # Psychedelic-specific interactions
        if therapy_type in ["psilocybin", "lsd", "mdma", "ketamine"]:

            # MAOI + Psychedelics - BLOCKING (dangerous)
            if "MAOI" in medication_classes:
                interactions.append({
                    "severity": "blocking",
                    "medication_class": "MAOI",
                    "message": "MAOIs (Monoamine Oxidase Inhibitors) can cause dangerous interactions with psychedelics, including serotonin syndrome",
                    "recommendation": "Discontinue MAOI for at least 2 weeks before psychedelic therapy"
                })

            # SSRI + Psychedelics - WARNING (may reduce efficacy)
            if "SSRI" in medication_classes:
                interactions.append({
                    "severity": "warning",
                    "medication_class": "SSRI",
                    "message": "SSRIs may reduce the effectiveness of psychedelic therapy",
                    "recommendation": "Consider tapering SSRI before therapy, consult with prescribing physician"
                })

            # SNRI + Psychedelics - WARNING
            if "SNRI" in medication_classes:
                interactions.append({
                    "severity": "warning",
                    "medication_class": "SNRI",
                    "message": "SNRIs may reduce the effectiveness of psychedelic therapy",
                    "recommendation": "Consider tapering SNRI before therapy, consult with prescribing physician"
                })

            # Lithium + Psychedelics - BLOCKING (seizure risk)
            if "Lithium" in medication_names or "Mood Stabilizer" in medication_classes:
                interactions.append({
                    "severity": "blocking",
                    "medication_class": "Mood Stabilizer",
                    "message": "Lithium and psychedelics can increase seizure risk",
                    "recommendation": "Do not combine lithium with psychedelic therapy"
                })

        # Hormone therapy interactions
        if therapy_type in ["testosterone", "estrogen", "growth_hormone"]:

            # Anticoagulants + Hormone therapy
            if "Anticoagulant" in medication_classes:
                interactions.append({
                    "severity": "warning",
                    "medication_class": "Anticoagulant",
                    "message": "Hormone therapy may affect blood clotting; anticoagulant dosing may need adjustment",
                    "recommendation": "Monitor INR/PT closely and adjust anticoagulant dose as needed"
                })

        # Invasive procedure interactions (stem cell, PRP, surgery, etc.)
        if therapy_type in ["stem_cell", "platelet_rich_plasma", "surgery"]:

            # Anticoagulants + Procedures
            if "Anticoagulant" in medication_classes:
                interactions.append({
                    "severity": "warning",
                    "medication_class": "Anticoagulant",
                    "message": "Anticoagulants increase bleeding risk during invasive procedures",
                    "recommendation": "Discontinue or bridge anticoagulation per procedural protocol"
                })

            # Antiplatelet agents + Procedures
            if "Antiplatelet" in medication_classes:
                interactions.append({
                    "severity": "warning",
                    "medication_class": "Antiplatelet",
                    "message": "Antiplatelet agents increase bleeding risk during invasive procedures",
                    "recommendation": "Consider discontinuing 5-7 days before procedure if safe"
                })

        # Chemotherapy interactions
        if therapy_type == "chemotherapy":

            # Warfarin + Chemotherapy
            if "Anticoagulant" in medication_classes:
                interactions.append({
                    "severity": "warning",
                    "medication_class": "Anticoagulant",
                    "message": "Chemotherapy can affect anticoagulation stability",
                    "recommendation": "Monitor INR more frequently during chemotherapy"
                })

        return interactions
