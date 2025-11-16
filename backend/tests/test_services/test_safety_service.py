import pytest
from app.services.safety_service import SafetyService
from app.models.protocol import SafetyCheck


class TestSafetyService:
    """Test suite for SafetyService."""

    def test_check_contraindications_no_issues(self):
        """Test checking contraindications when patient has no issues."""
        service = SafetyService()

        patient_data = {
            "age": 35,
            "diagnoses": ["F32.1"],  # Major depression
            "medications": [],
            "lab_values": {
                "hematocrit": 42.0,
                "hemoglobin": 14.5,
            },
            "vital_signs": {
                "blood_pressure_systolic": 120,
                "blood_pressure_diastolic": 80,
                "heart_rate": 72,
            }
        }

        safety_checks = [
            SafetyCheck(
                check_type="absolute_contraindication",
                condition={
                    "type": "diagnosis",
                    "value": "F20",  # Schizophrenia
                    "operator": "contains"
                },
                severity="blocking",
                override_allowed="false"
            )
        ]

        result = service.check_contraindications(patient_data, safety_checks)

        assert result["eligible"] is True
        assert result["risk_score"] == 0
        assert len(result["contraindications"]) == 0
        assert len(result["warnings"]) == 0


    def test_check_contraindications_blocking(self):
        """Test blocking contraindication (absolute contraindication)."""
        service = SafetyService()

        patient_data = {
            "age": 28,
            "diagnoses": ["F20.0"],  # Schizophrenia - absolute contraindication for psychedelics
            "medications": [],
        }

        safety_checks = [
            SafetyCheck(
                check_type="absolute_contraindication",
                condition={
                    "type": "diagnosis",
                    "value": "F20",
                    "operator": "contains"
                },
                severity="blocking",
                override_allowed="false"
            )
        ]

        result = service.check_contraindications(patient_data, safety_checks)

        assert result["eligible"] is False
        assert result["risk_score"] == 100
        assert len(result["contraindications"]) == 1
        assert result["contraindications"][0]["severity"] == "blocking"
        assert result["contraindications"][0]["check_type"] == "absolute_contraindication"


    def test_check_contraindications_warning(self):
        """Test warning contraindication (relative contraindication)."""
        service = SafetyService()

        patient_data = {
            "age": 28,
            "diagnoses": ["F31.0"],  # Bipolar disorder - relative contraindication
            "medications": [],
        }

        safety_checks = [
            SafetyCheck(
                check_type="relative_contraindication",
                condition={
                    "type": "diagnosis",
                    "value": "F31",
                    "operator": "contains"
                },
                severity="warning",
                override_allowed="true",
                override_requirements={"required_role": "medical_director"}
            )
        ]

        result = service.check_contraindications(patient_data, safety_checks)

        assert result["eligible"] is True  # Warnings don't block
        assert result["risk_score"] == 20  # Warnings add 20 points
        assert len(result["warnings"]) == 1
        assert result["warnings"][0]["override_allowed"] is True


    def test_evaluate_safety_check_diagnosis(self):
        """Test evaluating diagnosis-based safety check."""
        service = SafetyService()

        safety_check = SafetyCheck(
            check_type="absolute_contraindication",
            condition={
                "type": "diagnosis",
                "value": "F20",
                "operator": "contains"
            },
            severity="blocking",
            override_allowed="false"
        )

        patient_data = {"diagnoses": ["F20.0", "F32.1"]}

        result = service.evaluate_safety_check(safety_check, patient_data)

        assert result["triggered"] is True
        assert result["severity"] == "blocking"
        assert result["override_allowed"] is False


    def test_evaluate_safety_check_medication(self):
        """Test evaluating medication-based safety check."""
        service = SafetyService()

        safety_check = SafetyCheck(
            check_type="absolute_contraindication",
            condition={
                "type": "medication",
                "value": "SSRI",
                "operator": "class_match"
            },
            severity="blocking",
            override_allowed="false"
        )

        patient_data = {
            "medications": [
                {"name": "Sertraline", "class": "SSRI"},
                {"name": "Metformin", "class": "Antidiabetic"}
            ]
        }

        result = service.evaluate_safety_check(safety_check, patient_data)

        assert result["triggered"] is True


    def test_evaluate_safety_check_lab_value(self):
        """Test evaluating lab value-based safety check."""
        service = SafetyService()

        safety_check = SafetyCheck(
            check_type="relative_contraindication",
            condition={
                "type": "lab_value",
                "name": "hematocrit",
                "operator": "greater_than",
                "threshold": 52.0
            },
            severity="warning",
            override_allowed="true"
        )

        patient_data = {
            "lab_values": {
                "hematocrit": 54.0  # Elevated
            }
        }

        result = service.evaluate_safety_check(safety_check, patient_data)

        assert result["triggered"] is True
        assert result["severity"] == "warning"


    def test_evaluate_safety_check_age(self):
        """Test evaluating age-based safety check."""
        service = SafetyService()

        safety_check = SafetyCheck(
            check_type="absolute_contraindication",
            condition={
                "type": "age",
                "operator": "less_than",
                "threshold": 18
            },
            severity="blocking",
            override_allowed="false"
        )

        patient_data = {"age": 16}

        result = service.evaluate_safety_check(safety_check, patient_data)

        assert result["triggered"] is True


    def test_evaluate_safety_check_vital_sign(self):
        """Test evaluating vital sign-based safety check."""
        service = SafetyService()

        safety_check = SafetyCheck(
            check_type="relative_contraindication",
            condition={
                "type": "vital_sign",
                "name": "blood_pressure_systolic",
                "operator": "greater_than",
                "threshold": 140
            },
            severity="warning",
            override_allowed="true"
        )

        patient_data = {
            "vital_signs": {
                "blood_pressure_systolic": 152,
                "blood_pressure_diastolic": 92
            }
        }

        result = service.evaluate_safety_check(safety_check, patient_data)

        assert result["triggered"] is True


    def test_calculate_risk_score_no_issues(self):
        """Test risk score calculation with no issues."""
        service = SafetyService()

        risk_score = service.calculate_risk_score([], [], [])

        assert risk_score == 0


    def test_calculate_risk_score_with_blocking(self):
        """Test risk score calculation with blocking contraindication."""
        service = SafetyService()

        contraindications = [
            {"severity": "blocking", "message": "Active psychosis"}
        ]

        risk_score = service.calculate_risk_score(contraindications, [], [])

        assert risk_score == 100


    def test_calculate_risk_score_with_warnings(self):
        """Test risk score calculation with warnings."""
        service = SafetyService()

        warnings = [
            {"severity": "warning", "message": "Bipolar disorder"},
            {"severity": "warning", "message": "Family history of schizophrenia"}
        ]

        risk_score = service.calculate_risk_score([], warnings, [])

        assert risk_score == 40  # 20 + 20


    def test_calculate_risk_score_with_risk_factors(self):
        """Test risk score calculation with risk factors."""
        service = SafetyService()

        risk_factors = [
            {"severity": "info", "message": "First degree relative with addiction"},
            {"severity": "info", "message": "History of trauma"}
        ]

        risk_score = service.calculate_risk_score([], [], risk_factors)

        assert risk_score == 10  # 5 + 5


    def test_calculate_risk_score_combined(self):
        """Test risk score calculation with mixed issues (capped at 100)."""
        service = SafetyService()

        contraindications = [{"severity": "blocking"}]
        warnings = [{"severity": "warning"}, {"severity": "warning"}]
        risk_factors = [{"severity": "info"}]

        # Should be capped at 100 even though calculation would be higher
        risk_score = service.calculate_risk_score(contraindications, warnings, risk_factors)

        assert risk_score == 100


    def test_check_medication_interactions_ssri_psilocybin(self):
        """Test SSRI + psilocybin interaction detection."""
        service = SafetyService()

        patient_medications = [
            {"name": "Sertraline", "class": "SSRI"},
        ]

        interactions = service.check_medication_interactions(patient_medications, "psilocybin")

        assert len(interactions) > 0
        assert any("SSRI" in interaction["message"] for interaction in interactions)
        assert any(interaction["severity"] == "warning" for interaction in interactions)


    def test_check_medication_interactions_maoi_psychedelic(self):
        """Test MAOI + psychedelic interaction (blocking)."""
        service = SafetyService()

        patient_medications = [
            {"name": "Phenelzine", "class": "MAOI"},
        ]

        interactions = service.check_medication_interactions(patient_medications, "psilocybin")

        assert len(interactions) > 0
        assert any("MAOI" in interaction["message"] for interaction in interactions)
        assert any(interaction["severity"] == "blocking" for interaction in interactions)


    def test_check_medication_interactions_blood_thinners(self):
        """Test blood thinner interactions with procedures."""
        service = SafetyService()

        patient_medications = [
            {"name": "Warfarin", "class": "Anticoagulant"},
        ]

        interactions = service.check_medication_interactions(patient_medications, "stem_cell")

        assert len(interactions) > 0
        assert any("Anticoagulant" in interaction["message"] or "blood thinner" in interaction["message"].lower() for interaction in interactions)


    def test_multiple_contraindications(self):
        """Test multiple contraindications being detected."""
        service = SafetyService()

        patient_data = {
            "age": 17,  # Under 18
            "diagnoses": ["F31.0"],  # Bipolar
            "medications": [{"name": "Sertraline", "class": "SSRI"}],
            "vital_signs": {
                "blood_pressure_systolic": 155
            }
        }

        safety_checks = [
            SafetyCheck(
                check_type="absolute_contraindication",
                condition={"type": "age", "operator": "less_than", "threshold": 18},
                severity="blocking",
                override_allowed="false"
            ),
            SafetyCheck(
                check_type="relative_contraindication",
                condition={"type": "diagnosis", "value": "F31", "operator": "contains"},
                severity="warning",
                override_allowed="true"
            ),
            SafetyCheck(
                check_type="relative_contraindication",
                condition={"type": "vital_sign", "name": "blood_pressure_systolic", "operator": "greater_than", "threshold": 140},
                severity="warning",
                override_allowed="true"
            ),
        ]

        result = service.check_contraindications(patient_data, safety_checks)

        assert result["eligible"] is False  # Age is blocking
        assert len(result["contraindications"]) == 1
        assert len(result["warnings"]) == 2


    def test_real_world_psychosis_psychedelics(self):
        """Test real-world scenario: psychosis + psychedelics = absolute contraindication."""
        service = SafetyService()

        patient_data = {
            "age": 32,
            "diagnoses": ["F20.0"],  # Paranoid schizophrenia
            "medications": []
        }

        safety_checks = [
            SafetyCheck(
                check_type="absolute_contraindication",
                condition={"type": "diagnosis", "value": "F20", "operator": "contains"},
                severity="blocking",
                override_allowed="false"
            )
        ]

        result = service.check_contraindications(patient_data, safety_checks)

        assert result["eligible"] is False
        assert result["risk_score"] == 100
        assert "F20" in str(result["contraindications"])


    def test_real_world_elevated_hematocrit_testosterone(self):
        """Test real-world scenario: elevated hematocrit + testosterone."""
        service = SafetyService()

        patient_data = {
            "age": 45,
            "diagnoses": ["E29.1"],  # Hypogonadism
            "medications": [],
            "lab_values": {
                "hematocrit": 54.0  # Elevated (normal: 38.3-48.6%)
            }
        }

        safety_checks = [
            SafetyCheck(
                check_type="relative_contraindication",
                condition={"type": "lab_value", "name": "hematocrit", "operator": "greater_than", "threshold": 52.0},
                severity="warning",
                override_allowed="true",
                override_requirements={"required_intervention": "therapeutic_phlebotomy"}
            )
        ]

        result = service.check_contraindications(patient_data, safety_checks)

        assert result["eligible"] is True  # Warning, not blocking
        assert result["risk_score"] == 20
        assert len(result["warnings"]) == 1


    def test_real_world_chemotherapy_eligibility(self):
        """Test real-world scenario: chemotherapy eligibility based on organ function."""
        service = SafetyService()

        patient_data = {
            "age": 58,
            "diagnoses": ["C50.9"],  # Breast cancer
            "medications": [],
            "lab_values": {
                "creatinine_clearance": 45,  # Mild renal impairment (normal: >90)
                "absolute_neutrophil_count": 1200,  # Low (normal: >1500)
                "platelet_count": 90000  # Low (normal: >150,000)
            }
        }

        safety_checks = [
            SafetyCheck(
                check_type="absolute_contraindication",
                condition={"type": "lab_value", "name": "absolute_neutrophil_count", "operator": "less_than", "threshold": 1000},
                severity="blocking",
                override_allowed="false"
            ),
            SafetyCheck(
                check_type="relative_contraindication",
                condition={"type": "lab_value", "name": "platelet_count", "operator": "less_than", "threshold": 100000},
                severity="warning",
                override_allowed="true"
            )
        ]

        result = service.check_contraindications(patient_data, safety_checks)

        assert result["eligible"] is True  # ANC is 1200, above blocking threshold of 1000
        assert len(result["warnings"]) == 1  # Platelet warning
        assert result["risk_score"] == 20


    def test_medication_interaction_comprehensive(self):
        """Test comprehensive medication interaction checking."""
        service = SafetyService()

        patient_medications = [
            {"name": "Sertraline", "class": "SSRI"},
            {"name": "Warfarin", "class": "Anticoagulant"},
            {"name": "Metformin", "class": "Antidiabetic"}
        ]

        # Test with psilocybin
        psilocybin_interactions = service.check_medication_interactions(patient_medications, "psilocybin")
        assert len(psilocybin_interactions) > 0

        # Test with stem cell (invasive procedure)
        stem_cell_interactions = service.check_medication_interactions(patient_medications, "stem_cell")
        assert len(stem_cell_interactions) > 0

        # Test with ketamine (should have minimal interactions)
        ketamine_interactions = service.check_medication_interactions(patient_medications, "ketamine")
        # SSRI + ketamine may have interactions, but less severe than psilocybin
