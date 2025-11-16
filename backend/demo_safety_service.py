"""Demo script showing SafetyService in action with real-world scenarios."""

from app.services.safety_service import SafetyService
from app.models.protocol import SafetyCheck


def print_results(title: str, result: dict):
    """Print safety check results in a readable format."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Eligible: {result['eligible']}")
    print(f"Risk Score: {result['risk_score']}/100")

    if result['contraindications']:
        print(f"\nBLOCKING CONTRAINDICATIONS ({len(result['contraindications'])}):")
        for item in result['contraindications']:
            print(f"  - {item['message']}")
            print(f"    Override allowed: {item['override_allowed']}")

    if result['warnings']:
        print(f"\nWARNINGS ({len(result['warnings'])}):")
        for item in result['warnings']:
            print(f"  - {item['message']}")
            print(f"    Override allowed: {item['override_allowed']}")

    if result['risk_factors']:
        print(f"\nRISK FACTORS ({len(result['risk_factors'])}):")
        for item in result['risk_factors']:
            print(f"  - {item['message']}")


def demo_psychedelic_safety():
    """Demo: Psychedelic therapy safety screening."""
    print("\n" + "="*70)
    print("DEMO 1: PSILOCYBIN THERAPY SAFETY SCREENING")
    print("="*70)

    service = SafetyService()

    # Scenario 1: Ideal candidate
    patient1 = {
        "age": 35,
        "diagnoses": ["F32.1"],  # Major depressive disorder
        "medications": [],
        "vital_signs": {"blood_pressure_systolic": 120, "heart_rate": 72}
    }

    safety_checks = [
        SafetyCheck(
            check_type="absolute_contraindication",
            condition={"type": "diagnosis", "value": "F20", "operator": "contains"},
            severity="blocking",
            override_allowed="false"
        ),
        SafetyCheck(
            check_type="absolute_contraindication",
            condition={"type": "age", "operator": "less_than", "threshold": 18},
            severity="blocking",
            override_allowed="false"
        ),
    ]

    result1 = service.check_contraindications(patient1, safety_checks)
    print_results("Scenario 1: Ideal Candidate (Depression, no contraindications)", result1)

    # Scenario 2: Patient with schizophrenia (blocking)
    patient2 = {
        "age": 28,
        "diagnoses": ["F20.0"],  # Paranoid schizophrenia
        "medications": []
    }

    result2 = service.check_contraindications(patient2, safety_checks)
    print_results("Scenario 2: Patient with Schizophrenia (BLOCKED)", result2)

    # Scenario 3: Patient on SSRIs (warning)
    patient3 = {
        "age": 42,
        "diagnoses": ["F32.1"],
        "medications": [{"name": "Sertraline", "class": "SSRI"}]
    }

    ssri_check = SafetyCheck(
        check_type="relative_contraindication",
        condition={"type": "medication", "value": "SSRI", "operator": "class_match"},
        severity="warning",
        override_allowed="true",
        override_requirements={"recommendation": "Consider tapering"}
    )

    result3 = service.check_contraindications(patient3, safety_checks + [ssri_check])
    print_results("Scenario 3: Patient on SSRIs (Warning)", result3)

    # Check medication interactions
    interactions = service.check_medication_interactions(
        [{"name": "Sertraline", "class": "SSRI"}],
        "psilocybin"
    )
    print(f"\nMedication Interactions Found: {len(interactions)}")
    for interaction in interactions:
        print(f"  - [{interaction['severity'].upper()}] {interaction['message']}")


def demo_testosterone_therapy():
    """Demo: Testosterone therapy safety screening."""
    print("\n" + "="*70)
    print("DEMO 2: TESTOSTERONE THERAPY SAFETY SCREENING")
    print("="*70)

    service = SafetyService()

    # Patient with elevated hematocrit
    patient = {
        "age": 45,
        "diagnoses": ["E29.1"],  # Hypogonadism
        "medications": [],
        "lab_values": {
            "hematocrit": 54.0,  # Elevated
            "psa": 1.2  # Normal
        }
    }

    safety_checks = [
        SafetyCheck(
            check_type="relative_contraindication",
            condition={"type": "lab_value", "name": "hematocrit", "operator": "greater_than", "threshold": 52.0},
            severity="warning",
            override_allowed="true",
            override_requirements={"intervention": "therapeutic_phlebotomy"}
        ),
        SafetyCheck(
            check_type="absolute_contraindication",
            condition={"type": "lab_value", "name": "psa", "operator": "greater_than", "threshold": 4.0},
            severity="blocking",
            override_allowed="false"
        )
    ]

    result = service.check_contraindications(patient, safety_checks)
    print_results("Patient with Elevated Hematocrit", result)


def demo_chemotherapy_safety():
    """Demo: Chemotherapy safety screening."""
    print("\n" + "="*70)
    print("DEMO 3: CHEMOTHERAPY SAFETY SCREENING")
    print("="*70)

    service = SafetyService()

    # Patient with borderline organ function
    patient = {
        "age": 58,
        "diagnoses": ["C50.9"],  # Breast cancer
        "medications": [],
        "lab_values": {
            "creatinine_clearance": 45,  # Mild renal impairment
            "absolute_neutrophil_count": 1200,  # Low but above threshold
            "platelet_count": 90000,  # Low
            "bilirubin": 1.8  # Slightly elevated
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
            override_allowed="true",
            override_requirements={"intervention": "platelet_transfusion_if_bleeding"}
        ),
        SafetyCheck(
            check_type="relative_contraindication",
            condition={"type": "lab_value", "name": "creatinine_clearance", "operator": "less_than", "threshold": 60},
            severity="warning",
            override_allowed="true",
            override_requirements={"intervention": "dose_reduction"}
        )
    ]

    result = service.check_contraindications(patient, safety_checks)
    print_results("Patient with Borderline Organ Function", result)


def demo_medication_interactions():
    """Demo: Comprehensive medication interaction checking."""
    print("\n" + "="*70)
    print("DEMO 4: MEDICATION INTERACTION CHECKING")
    print("="*70)

    service = SafetyService()

    medications = [
        {"name": "Phenelzine", "class": "MAOI"},
        {"name": "Warfarin", "class": "Anticoagulant"},
        {"name": "Aspirin", "class": "Antiplatelet"}
    ]

    print("\nPatient Medications:")
    for med in medications:
        print(f"  - {med['name']} ({med['class']})")

    # Check interactions with different therapies
    therapies = ["psilocybin", "stem_cell", "testosterone"]

    for therapy in therapies:
        interactions = service.check_medication_interactions(medications, therapy)
        print(f"\n{therapy.upper()} Therapy - {len(interactions)} interactions found:")
        for interaction in interactions:
            print(f"  [{interaction['severity'].upper()}] {interaction['medication_class']}: {interaction['message']}")


if __name__ == "__main__":
    demo_psychedelic_safety()
    demo_testosterone_therapy()
    demo_chemotherapy_safety()
    demo_medication_interactions()

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
