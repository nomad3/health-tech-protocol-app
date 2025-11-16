"""
Demo: Protocol Execution Service

This demonstration showcases the protocol execution orchestration service,
including step progression, decision point handling, safety checks, and
complete protocol workflows.
"""

from datetime import datetime
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.protocol import Protocol, ProtocolStep, SafetyCheck, TherapyType, EvidenceLevel, StepType
from app.models.treatment import TreatmentPlan, TreatmentSession, SessionStatus, TreatmentStatus
from app.services.protocol_engine import ProtocolEngine


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def demo_linear_protocol_execution():
    """Demonstrate linear protocol execution workflow."""
    print_section("Demo 1: Linear Protocol Execution (Psilocybin for Depression)")

    db = SessionLocal()
    try:
        # Create users
        admin = User(
            email=f"admin_demo1_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.PLATFORM_ADMIN
        )
        patient = User(
            email=f"patient_demo1_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.PATIENT
        )
        therapist = User(
            email=f"therapist_demo1_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.THERAPIST
        )
        db.add_all([admin, patient, therapist])
        db.commit()

        # Create protocol with 4 steps
        protocol = Protocol(
            name="Psilocybin-Assisted Therapy for Depression",
            version="1.0",
            status="active",
            therapy_type=TherapyType.PSILOCYBIN,
            condition_treated="treatment_resistant_depression",
            evidence_level=EvidenceLevel.PHASE_3,
            created_by=admin.id
        )
        db.add(protocol)
        db.commit()

        steps = [
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=1,
                step_type=StepType.SCREENING,
                title="Psychiatric Evaluation & Medical Screening",
                description="Comprehensive assessment including mental health history, medical screening, and contraindication review"
            ),
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=2,
                step_type=StepType.PREPARATION,
                title="Preparatory Sessions (3 sessions)",
                description="Psychoeducation, intention setting, and rapport building"
            ),
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=3,
                step_type=StepType.DOSING,
                title="Psilocybin Dosing Session",
                description="6-8 hour dosing session with continuous monitoring"
            ),
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=4,
                step_type=StepType.INTEGRATION,
                title="Integration Sessions (3-6 sessions)",
                description="Process the experience and integrate insights into daily life"
            )
        ]
        db.add_all(steps)
        db.commit()

        print(f"Created protocol: {protocol.name}")
        print(f"Total steps: {len(steps)}")
        for step in steps:
            print(f"  Step {step.sequence_order}: {step.title} ({step.step_type.value})")

        # Create treatment plan
        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.SCREENING,
            start_date=datetime.utcnow()
        )
        db.add(plan)
        db.commit()

        print(f"\nCreated treatment plan for patient (ID: {patient.id})")
        print(f"Initial status: {plan.status.value}")

        # Initialize protocol engine
        engine = ProtocolEngine()

        # Execute protocol step by step
        print("\n--- Beginning Protocol Execution ---")

        current_step = engine.get_current_step(plan)
        step_num = 1

        while current_step is not None:
            print(f"\nStep {step_num}: {current_step.title}")
            print(f"  Type: {current_step.step_type.value}")
            print(f"  Status: Current step to be completed")

            # Check if can progress (safety checks)
            patient_data = {
                "age": 35,
                "diagnoses": ["F33.2"],  # Major depressive disorder, recurrent severe
                "medications": []
            }

            progression_check = engine.can_progress_to_step(plan, current_step, patient_data, db)
            print(f"  Can progress: {progression_check['can_progress']}")

            if not progression_check['can_progress']:
                print(f"  BLOCKED: {progression_check['blockers']}")
                break

            # Complete the session
            session = TreatmentSession(
                treatment_plan_id=plan.id,
                protocol_step_id=current_step.id,
                scheduled_at=datetime.utcnow(),
                actual_start=datetime.utcnow(),
                actual_end=datetime.utcnow(),
                therapist_id=therapist.id,
                location="in_person",
                status=SessionStatus.COMPLETED
            )
            db.add(session)
            db.commit()

            print(f"  Session completed!")

            # Update treatment plan status
            if step_num == 1:
                plan.status = TreatmentStatus.ACTIVE
                print(f"  Updated plan status: {plan.status.value}")

            # Get next step
            next_step = engine.get_next_step(protocol, current_step)
            if next_step:
                print(f"  Next: {next_step.title}")
            else:
                print(f"  Next: Protocol complete!")

            current_step = engine.get_current_step(plan)
            step_num += 1

        # Check completion
        is_complete = engine.is_protocol_complete(plan)
        print(f"\n--- Protocol Execution Complete ---")
        print(f"Is complete: {is_complete}")

        if is_complete:
            plan.status = TreatmentStatus.COMPLETED
            db.commit()
            print(f"Updated plan status: {plan.status.value}")

        print(f"\nTotal sessions completed: {len(plan.sessions)}")

    finally:
        db.rollback()
        db.close()


def demo_decision_point_protocol():
    """Demonstrate protocol with decision points."""
    print_section("Demo 2: Decision Point Protocol (MDMA for PTSD)")

    db = SessionLocal()
    try:
        # Create users
        admin = User(
            email=f"admin_demo2_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.PLATFORM_ADMIN
        )
        patient = User(
            email=f"patient_demo2_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.PATIENT
        )
        therapist = User(
            email=f"therapist_demo2_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.THERAPIST
        )
        db.add_all([admin, patient, therapist])
        db.commit()

        # Create protocol with decision point
        protocol = Protocol(
            name="MDMA-Assisted Therapy for PTSD",
            version="1.0",
            status="active",
            therapy_type=TherapyType.MDMA,
            condition_treated="ptsd",
            evidence_level=EvidenceLevel.PHASE_3,
            created_by=admin.id
        )
        db.add(protocol)
        db.commit()

        steps = [
            # Step 1: Screening
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=1,
                step_type=StepType.SCREENING,
                title="PTSD Assessment & Screening",
                description="CAPS-5 assessment and medical screening"
            ),
            # Step 2: Decision Point - Severity assessment
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=2,
                step_type=StepType.DECISION_POINT,
                title="Severity-Based Treatment Planning",
                description="Determine treatment intensity based on CAPS-5 score",
                evaluation_rules={
                    "type": "single_factor",
                    "factor": {
                        "factor": "caps5_score",
                        "operator": "in_range",
                        "ranges": [
                            {"min": 0, "max": 30, "value": "mild"},
                            {"min": 30, "max": 60, "value": "moderate"},
                            {"min": 60, "max": 100, "value": "severe"}
                        ]
                    }
                },
                branch_outcomes=[
                    {"outcome_id": "mild", "next_step_order": 3},
                    {"outcome_id": "moderate", "next_step_order": 4},
                    {"outcome_id": "severe", "next_step_order": 5}
                ]
            ),
            # Step 3: Mild path - 2 sessions
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=3,
                step_type=StepType.DOSING,
                title="Brief Protocol (2 MDMA sessions)",
                description="Two MDMA-assisted sessions for mild PTSD"
            ),
            # Step 4: Moderate path - 3 sessions (standard)
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=4,
                step_type=StepType.DOSING,
                title="Standard Protocol (3 MDMA sessions)",
                description="Three MDMA-assisted sessions for moderate PTSD"
            ),
            # Step 5: Severe path - 4 sessions + intensive prep
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=5,
                step_type=StepType.DOSING,
                title="Intensive Protocol (4 MDMA sessions)",
                description="Four MDMA-assisted sessions with extended preparation for severe PTSD"
            )
        ]
        db.add_all(steps)
        db.commit()

        print(f"Created protocol: {protocol.name}")
        print(f"Total steps: {len(steps)}")
        print(f"\nProtocol structure:")
        print(f"  Step 1: {steps[0].title}")
        print(f"  Step 2: {steps[1].title} (DECISION POINT)")
        print(f"    - Mild (CAPS-5 < 30) -> Step 3: {steps[2].title}")
        print(f"    - Moderate (CAPS-5 30-60) -> Step 4: {steps[3].title}")
        print(f"    - Severe (CAPS-5 > 60) -> Step 5: {steps[4].title}")

        # Simulate three different patient scenarios
        scenarios = [
            {"caps5_score": 25, "expected_path": "mild", "expected_step": 3},
            {"caps5_score": 45, "expected_path": "moderate", "expected_step": 4},
            {"caps5_score": 75, "expected_path": "severe", "expected_step": 5}
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n--- Scenario {i}: CAPS-5 Score = {scenario['caps5_score']} ---")

            # Create treatment plan
            plan = TreatmentPlan(
                patient_id=patient.id,
                therapist_id=therapist.id,
                protocol_id=protocol.id,
                protocol_version="1.0",
                status=TreatmentStatus.SCREENING,
                start_date=datetime.utcnow()
            )
            db.add(plan)
            db.commit()

            engine = ProtocolEngine()

            # Complete screening (step 1)
            session1 = TreatmentSession(
                treatment_plan_id=plan.id,
                protocol_step_id=steps[0].id,
                scheduled_at=datetime.utcnow(),
                therapist_id=therapist.id,
                location="in_person",
                status=SessionStatus.COMPLETED
            )
            db.add(session1)
            db.commit()

            print(f"Completed: {steps[0].title}")

            # Get decision point (step 2)
            decision_step = engine.get_current_step(plan)
            print(f"Current step: {decision_step.title}")

            # Evaluate decision point
            patient_data = {"caps5_score": scenario['caps5_score']}
            outcome = engine.evaluate_decision_point(decision_step, patient_data)
            print(f"Decision outcome: {outcome} (expected: {scenario['expected_path']})")

            # Get next step based on outcome
            next_step = engine.get_next_step(protocol, decision_step, patient_data)
            print(f"Branching to: Step {next_step.sequence_order} - {next_step.title}")

            assert next_step.sequence_order == scenario['expected_step'], \
                f"Expected step {scenario['expected_step']}, got {next_step.sequence_order}"

            print(f"Result: SUCCESS - Correctly branched to {scenario['expected_path']} treatment path")

            # Cleanup
            db.delete(plan)
            db.commit()

    finally:
        db.rollback()
        db.close()


def demo_safety_checks():
    """Demonstrate safety checks blocking progression."""
    print_section("Demo 3: Safety Checks & Contraindications")

    db = SessionLocal()
    try:
        # Create users
        admin = User(
            email=f"admin_demo3_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.PLATFORM_ADMIN
        )
        patient = User(
            email=f"patient_demo3_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.PATIENT
        )
        therapist = User(
            email=f"therapist_demo3_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.THERAPIST
        )
        db.add_all([admin, patient, therapist])
        db.commit()

        # Create protocol
        protocol = Protocol(
            name="Psilocybin Protocol with Safety Checks",
            version="1.0",
            status="active",
            therapy_type=TherapyType.PSILOCYBIN,
            condition_treated="depression",
            evidence_level=EvidenceLevel.PHASE_3,
            created_by=admin.id
        )
        db.add(protocol)
        db.commit()

        # Create step with safety checks
        step = ProtocolStep(
            protocol_id=protocol.id,
            sequence_order=1,
            step_type=StepType.DOSING,
            title="Psilocybin Dosing Session"
        )
        db.add(step)
        db.commit()

        # Add safety checks
        safety_checks = [
            SafetyCheck(
                protocol_step_id=step.id,
                check_type="absolute_contraindication",
                condition={
                    "type": "diagnosis",
                    "value": "F20",  # Schizophrenia
                    "operator": "contains"
                },
                severity="blocking",
                override_allowed="false",
                evidence_source="Psilocybin can exacerbate psychotic symptoms"
            ),
            SafetyCheck(
                protocol_step_id=step.id,
                check_type="relative_contraindication",
                condition={
                    "type": "medication",
                    "value": "SSRI",
                    "operator": "class_match"
                },
                severity="warning",
                override_allowed="true",
                evidence_source="SSRIs may reduce psilocybin efficacy"
            ),
            SafetyCheck(
                protocol_step_id=step.id,
                check_type="risk_factor",
                condition={
                    "type": "vital_sign",
                    "name": "systolic_bp",
                    "operator": "greater_than",
                    "threshold": 140
                },
                severity="info",
                override_allowed="true",
                evidence_source="Monitor BP closely during session"
            )
        ]
        db.add_all(safety_checks)
        db.commit()

        print(f"Created protocol with {len(safety_checks)} safety checks:")
        for sc in safety_checks:
            print(f"  - {sc.check_type}: {sc.severity}")

        # Test scenarios
        scenarios = [
            {
                "name": "Healthy patient",
                "data": {
                    "age": 30,
                    "diagnoses": ["F33.2"],  # Depression
                    "medications": [],
                    "vital_signs": {"systolic_bp": 120}
                },
                "expected_progress": True,
                "expected_blockers": 0,
                "expected_warnings": 0
            },
            {
                "name": "Patient with schizophrenia (BLOCKED)",
                "data": {
                    "age": 30,
                    "diagnoses": ["F20.0"],  # Schizophrenia
                    "medications": [],
                    "vital_signs": {"systolic_bp": 120}
                },
                "expected_progress": False,
                "expected_blockers": 1,
                "expected_warnings": 0
            },
            {
                "name": "Patient on SSRI (WARNING)",
                "data": {
                    "age": 30,
                    "diagnoses": ["F33.2"],
                    "medications": [{"name": "Sertraline", "class": "SSRI"}],
                    "vital_signs": {"systolic_bp": 120}
                },
                "expected_progress": True,
                "expected_blockers": 0,
                "expected_warnings": 1
            },
            {
                "name": "Patient with high BP (INFO)",
                "data": {
                    "age": 30,
                    "diagnoses": ["F33.2"],
                    "medications": [],
                    "vital_signs": {"systolic_bp": 150}
                },
                "expected_progress": True,
                "expected_blockers": 0,
                "expected_warnings": 0
            }
        ]

        engine = ProtocolEngine()

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n--- Scenario {i}: {scenario['name']} ---")

            # Create treatment plan
            plan = TreatmentPlan(
                patient_id=patient.id,
                therapist_id=therapist.id,
                protocol_id=protocol.id,
                protocol_version="1.0",
                status=TreatmentStatus.ACTIVE,
                start_date=datetime.utcnow()
            )
            db.add(plan)
            db.commit()

            # Check progression
            result = engine.can_progress_to_step(plan, step, scenario['data'], db)

            print(f"Can progress: {result['can_progress']}")
            print(f"Blockers: {len(result['blockers'])}")
            print(f"Warnings: {len(result['warnings'])}")
            print(f"Risk factors: {len(result['risk_factors'])}")

            if result['blockers']:
                for blocker in result['blockers']:
                    print(f"  BLOCKER: {blocker['message']}")

            if result['warnings']:
                for warning in result['warnings']:
                    print(f"  WARNING: {warning['message']}")

            if result['risk_factors']:
                for risk in result['risk_factors']:
                    print(f"  INFO: {risk['message']}")

            # Verify expectations
            assert result['can_progress'] == scenario['expected_progress']
            assert len(result['blockers']) == scenario['expected_blockers']
            assert len(result['warnings']) == scenario['expected_warnings']

            print(f"Result: PASSED")

            # Cleanup
            db.delete(plan)
            db.commit()

    finally:
        db.rollback()
        db.close()


def demo_multi_therapy_types():
    """Demonstrate protocol execution with different therapy types."""
    print_section("Demo 4: Multiple Therapy Types")

    db = SessionLocal()
    try:
        admin = User(
            email=f"admin_demo4_{int(datetime.utcnow().timestamp())}@test.com",
            password_hash="hash",
            role=UserRole.PLATFORM_ADMIN
        )
        db.add(admin)
        db.commit()

        # Create protocols for different therapy types
        protocols = [
            {
                "name": "Testosterone Replacement Therapy",
                "therapy_type": TherapyType.TESTOSTERONE,
                "condition": "hypogonadism",
                "steps": ["Lab Work", "Initial Dose", "6-Week Follow-up", "12-Week Follow-up"]
            },
            {
                "name": "FOLFOX Chemotherapy",
                "therapy_type": TherapyType.CHEMOTHERAPY,
                "condition": "colorectal_cancer",
                "steps": [f"Cycle {i}" for i in range(1, 7)]
            },
            {
                "name": "Ketamine Infusion Protocol",
                "therapy_type": TherapyType.KETAMINE,
                "condition": "treatment_resistant_depression",
                "steps": ["Assessment", "Infusion 1", "Infusion 2", "Infusion 3", "Follow-up"]
            }
        ]

        for proto_def in protocols:
            print(f"\n{proto_def['name']}:")
            print(f"  Therapy type: {proto_def['therapy_type'].value}")
            print(f"  Condition: {proto_def['condition']}")
            print(f"  Total steps: {len(proto_def['steps'])}")

            protocol = Protocol(
                name=proto_def['name'],
                version="1.0",
                status="active",
                therapy_type=proto_def['therapy_type'],
                condition_treated=proto_def['condition'],
                evidence_level=EvidenceLevel.FDA_APPROVED,
                created_by=admin.id
            )
            db.add(protocol)
            db.commit()

            for i, step_title in enumerate(proto_def['steps'], 1):
                step = ProtocolStep(
                    protocol_id=protocol.id,
                    sequence_order=i,
                    step_type=StepType.DOSING if i > 1 else StepType.SCREENING,
                    title=step_title
                )
                db.add(step)
                print(f"    Step {i}: {step_title}")
            db.commit()

            print(f"  Protocol created successfully!")

    finally:
        db.rollback()
        db.close()


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("  Protocol Execution Service - Demonstration Suite")
    print("=" * 80)
    print("\nThis demo showcases the complete protocol execution orchestration,")
    print("including step progression, decision points, safety checks, and workflows")
    print("across multiple therapy types.")

    try:
        demo_linear_protocol_execution()
        demo_decision_point_protocol()
        demo_safety_checks()
        demo_multi_therapy_types()

        print_section("All Demonstrations Complete!")
        print("Summary:")
        print("  1. Linear Protocol Execution: Demonstrated step-by-step progression")
        print("  2. Decision Point Protocol: Showed branching logic based on severity")
        print("  3. Safety Checks: Validated contraindication blocking and warnings")
        print("  4. Multiple Therapy Types: Created protocols for various treatments")
        print("\nProtocol execution service is working correctly!")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
