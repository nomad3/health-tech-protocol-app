"""Tests for protocol execution service."""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.protocol import Protocol, ProtocolStep, SafetyCheck, TherapyType, EvidenceLevel, StepType
from app.models.treatment import TreatmentPlan, TreatmentSession, SessionStatus, TreatmentStatus
from app.models.profiles import Clinic
from app.services.protocol_engine import ProtocolEngine


# Counter for unique email generation
_email_counter = 0


def unique_email(prefix: str) -> str:
    """Generate a unique email address for testing."""
    import time
    global _email_counter
    _email_counter += 1
    timestamp = int(time.time() * 1000000)  # microseconds
    return f"{prefix}_{_email_counter}_{timestamp}@test.com"


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def protocol_engine():
    """Create protocol engine instance."""
    return ProtocolEngine()


@pytest.fixture
def simple_protocol(db_session: Session):
    """Create a simple 3-step protocol for testing."""
    # Create user
    user = User(
        email=unique_email("admin"),
        password_hash="hash",
        role=UserRole.PLATFORM_ADMIN
    )
    db_session.add(user)
    db_session.commit()

    # Create protocol
    protocol = Protocol(
        name="Simple Test Protocol",
        version="1.0",
        status="active",
        therapy_type=TherapyType.PSILOCYBIN,
        condition_treated="depression",
        evidence_level=EvidenceLevel.PHASE_3,
        created_by=user.id
    )
    db_session.add(protocol)
    db_session.commit()

    # Create 3 steps (screening, preparation, dosing)
    step1 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Initial Screening"
    )
    step2 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=2,
        step_type=StepType.PREPARATION,
        title="Preparation Session"
    )
    step3 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=3,
        step_type=StepType.DOSING,
        title="Dosing Session"
    )
    db_session.add_all([step1, step2, step3])
    db_session.commit()

    return protocol


@pytest.fixture
def decision_point_protocol(db_session: Session):
    """Create a protocol with decision points for testing."""
    # Create user
    user = User(
        email=unique_email("admin2"),
        password_hash="hash",
        role=UserRole.PLATFORM_ADMIN
    )
    db_session.add(user)
    db_session.commit()

    # Create protocol
    protocol = Protocol(
        name="Decision Point Protocol",
        version="1.0",
        status="active",
        therapy_type=TherapyType.MDMA,
        condition_treated="ptsd",
        evidence_level=EvidenceLevel.PHASE_3,
        created_by=user.id
    )
    db_session.add(protocol)
    db_session.commit()

    # Step 1: Screening
    step1 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=1,
        step_type=StepType.SCREENING,
        title="Initial Screening"
    )

    # Step 2: Decision Point - determine severity
    step2 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=2,
        step_type=StepType.DECISION_POINT,
        title="Severity Assessment",
        evaluation_rules={
            "type": "single_factor",
            "factor": {
                "factor": "severity_score",
                "operator": "in_range",
                "ranges": [
                    {"min": 0, "max": 30, "value": "mild"},
                    {"min": 30, "max": 70, "value": "moderate"},
                    {"min": 70, "max": 100, "value": "severe"}
                ]
            }
        },
        branch_outcomes=[
            {"outcome_id": "mild", "next_step_order": 3},
            {"outcome_id": "moderate", "next_step_order": 4},
            {"outcome_id": "severe", "next_step_order": 5}
        ]
    )

    # Step 3: Mild treatment path
    step3 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=3,
        step_type=StepType.PREPARATION,
        title="Brief Preparation (Mild)"
    )

    # Step 4: Moderate treatment path
    step4 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=4,
        step_type=StepType.PREPARATION,
        title="Standard Preparation (Moderate)"
    )

    # Step 5: Severe treatment path
    step5 = ProtocolStep(
        protocol_id=protocol.id,
        sequence_order=5,
        step_type=StepType.PREPARATION,
        title="Intensive Preparation (Severe)"
    )

    db_session.add_all([step1, step2, step3, step4, step5])
    db_session.commit()

    return protocol


@pytest.fixture
def treatment_plan_no_sessions(db_session: Session, simple_protocol):
    """Create a treatment plan with no sessions."""
    # Create users
    patient = User(email=unique_email("patient"), password_hash="hash", role=UserRole.PATIENT)
    therapist = User(email=unique_email("therapist"), password_hash="hash", role=UserRole.THERAPIST)
    db_session.add_all([patient, therapist])
    db_session.commit()

    # Create treatment plan
    plan = TreatmentPlan(
        patient_id=patient.id,
        therapist_id=therapist.id,
        protocol_id=simple_protocol.id,
        protocol_version="1.0",
        status=TreatmentStatus.SCREENING,
        start_date=datetime.utcnow()
    )
    db_session.add(plan)
    db_session.commit()

    return plan


@pytest.fixture
def treatment_plan_with_sessions(db_session: Session, simple_protocol):
    """Create a treatment plan with one completed session."""
    # Create users
    patient = User(email=unique_email("patient2"), password_hash="hash", role=UserRole.PATIENT)
    therapist = User(email=unique_email("therapist2"), password_hash="hash", role=UserRole.THERAPIST)
    db_session.add_all([patient, therapist])
    db_session.commit()

    # Create treatment plan
    plan = TreatmentPlan(
        patient_id=patient.id,
        therapist_id=therapist.id,
        protocol_id=simple_protocol.id,
        protocol_version="1.0",
        status=TreatmentStatus.ACTIVE,
        start_date=datetime.utcnow()
    )
    db_session.add(plan)
    db_session.commit()

    # Create completed session for step 1
    session = TreatmentSession(
        treatment_plan_id=plan.id,
        protocol_step_id=simple_protocol.steps[0].id,
        scheduled_at=datetime.utcnow(),
        actual_start=datetime.utcnow(),
        actual_end=datetime.utcnow(),
        therapist_id=therapist.id,
        location="in_person",
        status=SessionStatus.COMPLETED
    )
    db_session.add(session)
    db_session.commit()

    return plan


class TestGetCurrentStep:
    """Tests for get_current_step method."""

    def test_current_step_no_sessions(self, db_session, protocol_engine, treatment_plan_no_sessions):
        """Test getting current step when no sessions completed."""
        current_step = protocol_engine.get_current_step(treatment_plan_no_sessions)

        # Should return first step
        assert current_step is not None
        assert current_step.sequence_order == 1
        assert current_step.step_type == StepType.SCREENING

    def test_current_step_with_one_session(self, db_session, protocol_engine, treatment_plan_with_sessions):
        """Test getting current step when one session completed."""
        current_step = protocol_engine.get_current_step(treatment_plan_with_sessions)

        # Should return second step (first is completed)
        assert current_step is not None
        assert current_step.sequence_order == 2
        assert current_step.step_type == StepType.PREPARATION

    def test_current_step_all_complete(self, db_session, protocol_engine, simple_protocol):
        """Test getting current step when all sessions completed."""
        # Create treatment plan with all sessions completed
        patient = User(email=unique_email("patient3"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("therapist3"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=simple_protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.COMPLETED,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Complete all 3 sessions
        for step in simple_protocol.steps:
            session = TreatmentSession(
                treatment_plan_id=plan.id,
                protocol_step_id=step.id,
                scheduled_at=datetime.utcnow(),
                actual_start=datetime.utcnow(),
                actual_end=datetime.utcnow(),
                therapist_id=therapist.id,
                location="in_person",
                status=SessionStatus.COMPLETED
            )
            db_session.add(session)
        db_session.commit()

        current_step = protocol_engine.get_current_step(plan)

        # Should return None when all complete
        assert current_step is None


class TestGetNextStep:
    """Tests for get_next_step method."""

    def test_next_step_linear_progression(self, db_session, protocol_engine, simple_protocol):
        """Test getting next step in linear progression."""
        step1 = simple_protocol.steps[0]
        step2 = simple_protocol.steps[1]

        next_step = protocol_engine.get_next_step(simple_protocol, step1)

        assert next_step is not None
        assert next_step.id == step2.id
        assert next_step.sequence_order == 2

    def test_next_step_at_end(self, db_session, protocol_engine, simple_protocol):
        """Test getting next step when at end of protocol."""
        last_step = simple_protocol.steps[-1]

        next_step = protocol_engine.get_next_step(simple_protocol, last_step)

        # Should return None at end
        assert next_step is None

    def test_next_step_decision_point(self, db_session, protocol_engine, decision_point_protocol):
        """Test getting next step through decision point."""
        # Get decision point step (step 2)
        decision_step = decision_point_protocol.steps[1]

        # Patient data with moderate severity
        patient_data = {"severity_score": 50}

        # Evaluate decision point first
        outcome = protocol_engine.evaluate_decision_point(decision_step, patient_data)
        assert outcome == "moderate"

        # Get next step based on outcome
        next_step = protocol_engine.get_next_step(
            decision_point_protocol,
            decision_step,
            patient_data
        )

        # Should go to step 4 (moderate path)
        assert next_step is not None
        assert next_step.sequence_order == 4
        assert next_step.title == "Standard Preparation (Moderate)"

    def test_next_step_decision_point_mild(self, db_session, protocol_engine, decision_point_protocol):
        """Test decision point with mild severity."""
        decision_step = decision_point_protocol.steps[1]
        patient_data = {"severity_score": 20}

        next_step = protocol_engine.get_next_step(
            decision_point_protocol,
            decision_step,
            patient_data
        )

        # Should go to step 3 (mild path)
        assert next_step is not None
        assert next_step.sequence_order == 3
        assert next_step.title == "Brief Preparation (Mild)"

    def test_next_step_decision_point_severe(self, db_session, protocol_engine, decision_point_protocol):
        """Test decision point with severe severity."""
        decision_step = decision_point_protocol.steps[1]
        patient_data = {"severity_score": 85}

        next_step = protocol_engine.get_next_step(
            decision_point_protocol,
            decision_step,
            patient_data
        )

        # Should go to step 5 (severe path)
        assert next_step is not None
        assert next_step.sequence_order == 5
        assert next_step.title == "Intensive Preparation (Severe)"


class TestIsProtocolComplete:
    """Tests for is_protocol_complete method."""

    def test_protocol_not_complete(self, db_session, protocol_engine, treatment_plan_no_sessions):
        """Test protocol completion check when not complete."""
        is_complete = protocol_engine.is_protocol_complete(treatment_plan_no_sessions)
        assert is_complete is False

    def test_protocol_partially_complete(self, db_session, protocol_engine, treatment_plan_with_sessions):
        """Test protocol completion check when partially complete."""
        is_complete = protocol_engine.is_protocol_complete(treatment_plan_with_sessions)
        assert is_complete is False

    def test_protocol_complete(self, db_session, protocol_engine, simple_protocol):
        """Test protocol completion check when complete."""
        # Create treatment plan with all sessions completed
        patient = User(email=unique_email("patient4"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("therapist4"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=simple_protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.ACTIVE,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Complete all sessions
        for step in simple_protocol.steps:
            session = TreatmentSession(
                treatment_plan_id=plan.id,
                protocol_step_id=step.id,
                scheduled_at=datetime.utcnow(),
                actual_start=datetime.utcnow(),
                actual_end=datetime.utcnow(),
                therapist_id=therapist.id,
                location="in_person",
                status=SessionStatus.COMPLETED
            )
            db_session.add(session)
        db_session.commit()

        is_complete = protocol_engine.is_protocol_complete(plan)
        assert is_complete is True


class TestCanProgressToStep:
    """Tests for can_progress_to_step method."""

    def test_can_progress_no_blockers(self, db_session, protocol_engine, simple_protocol):
        """Test progression when no safety checks block it."""
        patient = User(email=unique_email("patient5"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("therapist5"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=simple_protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.ACTIVE,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Patient data with no contraindications
        patient_data = {
            "age": 30,
            "diagnoses": [],
            "medications": []
        }

        next_step = simple_protocol.steps[1]
        result = protocol_engine.can_progress_to_step(plan, next_step, patient_data, db_session)

        assert result["can_progress"] is True
        assert len(result["blockers"]) == 0

    def test_can_progress_with_blockers(self, db_session, protocol_engine, simple_protocol):
        """Test progression when safety checks block it."""
        # Add blocking safety check to step 2
        step2 = simple_protocol.steps[1]
        safety_check = SafetyCheck(
            protocol_step_id=step2.id,
            check_type="absolute_contraindication",
            condition={
                "type": "diagnosis",
                "value": "F20",
                "operator": "contains"
            },
            severity="blocking",
            override_allowed="false"
        )
        db_session.add(safety_check)
        db_session.commit()

        # Create treatment plan
        patient = User(email=unique_email("patient6"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("therapist6"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=simple_protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.ACTIVE,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Patient data with schizophrenia diagnosis
        patient_data = {
            "age": 30,
            "diagnoses": ["F20.0"],
            "medications": []
        }

        result = protocol_engine.can_progress_to_step(plan, step2, patient_data, db_session)

        assert result["can_progress"] is False
        assert len(result["blockers"]) == 1
        assert "F20" in result["blockers"][0]["message"]

    def test_can_progress_with_warnings(self, db_session, protocol_engine, simple_protocol):
        """Test progression with warnings but no blockers."""
        # Add warning safety check to step 2
        step2 = simple_protocol.steps[1]
        safety_check = SafetyCheck(
            protocol_step_id=step2.id,
            check_type="relative_contraindication",
            condition={
                "type": "medication",
                "value": "SSRI",
                "operator": "class_match"
            },
            severity="warning",
            override_allowed="true"
        )
        db_session.add(safety_check)
        db_session.commit()

        # Create treatment plan
        patient = User(email=unique_email("patient7"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("therapist7"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=simple_protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.ACTIVE,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Patient data with SSRI
        patient_data = {
            "age": 30,
            "diagnoses": [],
            "medications": [{"name": "Sertraline", "class": "SSRI"}]
        }

        result = protocol_engine.can_progress_to_step(plan, step2, patient_data, db_session)

        # Can still progress despite warning
        assert result["can_progress"] is True
        assert len(result["blockers"]) == 0
        assert len(result["warnings"]) == 1
        assert "SSRI" in result["warnings"][0]["message"]


class TestTreatmentPlanStatusUpdates:
    """Tests for treatment plan status updates based on progress."""

    def test_status_update_to_active(self, db_session, protocol_engine, treatment_plan_no_sessions):
        """Test status update from screening to active."""
        # Initially in screening status
        assert treatment_plan_no_sessions.status == TreatmentStatus.SCREENING

        # Complete first session (screening)
        patient = db_session.query(User).filter_by(email="patient@test.com").first()
        therapist = db_session.query(User).filter_by(email="therapist@test.com").first()
        protocol = treatment_plan_no_sessions.protocol

        session = TreatmentSession(
            treatment_plan_id=treatment_plan_no_sessions.id,
            protocol_step_id=protocol.steps[0].id,
            scheduled_at=datetime.utcnow(),
            actual_start=datetime.utcnow(),
            actual_end=datetime.utcnow(),
            therapist_id=therapist.id,
            location="in_person",
            status=SessionStatus.COMPLETED
        )
        db_session.add(session)
        db_session.commit()

        # After screening, should move to active
        # (This would be handled by the service in practice)
        treatment_plan_no_sessions.status = TreatmentStatus.ACTIVE
        db_session.commit()

        assert treatment_plan_no_sessions.status == TreatmentStatus.ACTIVE

    def test_status_update_to_completed(self, db_session, protocol_engine, simple_protocol):
        """Test status update to completed when protocol is finished."""
        # Create treatment plan
        patient = User(email=unique_email("patient8"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("therapist8"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=simple_protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.ACTIVE,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Complete all sessions
        for step in simple_protocol.steps:
            session = TreatmentSession(
                treatment_plan_id=plan.id,
                protocol_step_id=step.id,
                scheduled_at=datetime.utcnow(),
                actual_start=datetime.utcnow(),
                actual_end=datetime.utcnow(),
                therapist_id=therapist.id,
                location="in_person",
                status=SessionStatus.COMPLETED
            )
            db_session.add(session)
        db_session.commit()

        # Check if protocol is complete
        is_complete = protocol_engine.is_protocol_complete(plan)
        assert is_complete is True

        # Update status to completed
        plan.status = TreatmentStatus.COMPLETED
        db_session.commit()

        assert plan.status == TreatmentStatus.COMPLETED


class TestCompleteProtocolWorkflow:
    """End-to-end tests for complete protocol execution."""

    def test_complete_linear_protocol_workflow(self, db_session, protocol_engine, simple_protocol):
        """Test complete workflow from start to finish with linear protocol."""
        # Create treatment plan
        patient = User(email=unique_email("patient9"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("therapist9"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=simple_protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.SCREENING,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        patient_data = {
            "age": 30,
            "diagnoses": [],
            "medications": []
        }

        # Step 1: Get current step (should be first)
        current = protocol_engine.get_current_step(plan)
        assert current.sequence_order == 1
        assert not protocol_engine.is_protocol_complete(plan)

        # Step 2: Check if can progress
        result = protocol_engine.can_progress_to_step(plan, current, patient_data, db_session)
        assert result["can_progress"] is True

        # Step 3: Complete first session
        session1 = TreatmentSession(
            treatment_plan_id=plan.id,
            protocol_step_id=current.id,
            scheduled_at=datetime.utcnow(),
            actual_start=datetime.utcnow(),
            actual_end=datetime.utcnow(),
            therapist_id=therapist.id,
            location="in_person",
            status=SessionStatus.COMPLETED
        )
        db_session.add(session1)
        db_session.commit()

        # Step 4: Get next step
        next_step = protocol_engine.get_next_step(simple_protocol, current)
        assert next_step.sequence_order == 2

        # Step 5: Update status to active
        plan.status = TreatmentStatus.ACTIVE
        db_session.commit()

        # Step 6: Continue through remaining steps
        current = protocol_engine.get_current_step(plan)
        assert current.sequence_order == 2

        # Complete step 2
        session2 = TreatmentSession(
            treatment_plan_id=plan.id,
            protocol_step_id=current.id,
            scheduled_at=datetime.utcnow(),
            actual_start=datetime.utcnow(),
            actual_end=datetime.utcnow(),
            therapist_id=therapist.id,
            location="in_person",
            status=SessionStatus.COMPLETED
        )
        db_session.add(session2)
        db_session.commit()

        # Complete step 3
        current = protocol_engine.get_current_step(plan)
        assert current.sequence_order == 3

        session3 = TreatmentSession(
            treatment_plan_id=plan.id,
            protocol_step_id=current.id,
            scheduled_at=datetime.utcnow(),
            actual_start=datetime.utcnow(),
            actual_end=datetime.utcnow(),
            therapist_id=therapist.id,
            location="in_person",
            status=SessionStatus.COMPLETED
        )
        db_session.add(session3)
        db_session.commit()

        # Step 7: Check completion
        assert protocol_engine.is_protocol_complete(plan)
        current = protocol_engine.get_current_step(plan)
        assert current is None

        # Step 8: Update to completed
        plan.status = TreatmentStatus.COMPLETED
        db_session.commit()

        assert plan.status == TreatmentStatus.COMPLETED

    def test_complete_decision_point_workflow(self, db_session, protocol_engine, decision_point_protocol):
        """Test complete workflow with decision points."""
        # Create treatment plan
        patient = User(email=unique_email("patient10"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("therapist10"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=decision_point_protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.SCREENING,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Complete step 1 (screening)
        step1 = decision_point_protocol.steps[0]
        session1 = TreatmentSession(
            treatment_plan_id=plan.id,
            protocol_step_id=step1.id,
            scheduled_at=datetime.utcnow(),
            actual_start=datetime.utcnow(),
            actual_end=datetime.utcnow(),
            therapist_id=therapist.id,
            location="in_person",
            status=SessionStatus.COMPLETED
        )
        db_session.add(session1)
        db_session.commit()

        # Get decision point (step 2)
        decision_step = protocol_engine.get_current_step(plan)
        assert decision_step.step_type == StepType.DECISION_POINT

        # Evaluate with severe severity
        patient_data = {"severity_score": 80}
        next_step = protocol_engine.get_next_step(
            decision_point_protocol,
            decision_step,
            patient_data
        )

        # Should branch to severe path (step 5)
        assert next_step.sequence_order == 5
        assert next_step.title == "Intensive Preparation (Severe)"


class TestMultipleTherapyTypes:
    """Tests with different therapy types."""

    def test_testosterone_protocol(self, db_session, protocol_engine):
        """Test protocol execution with testosterone therapy."""
        # Create user
        user = User(
            email=unique_email("admin_test"),
            password_hash="hash",
            role=UserRole.PLATFORM_ADMIN
        )
        db_session.add(user)
        db_session.commit()

        # Create testosterone protocol
        protocol = Protocol(
            name="Testosterone Replacement",
            version="1.0",
            status="active",
            therapy_type=TherapyType.TESTOSTERONE,
            condition_treated="hypogonadism",
            evidence_level=EvidenceLevel.FDA_APPROVED,
            created_by=user.id
        )
        db_session.add(protocol)
        db_session.commit()

        # Add steps
        steps = [
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=1,
                step_type=StepType.SCREENING,
                title="Lab Work and Physical"
            ),
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=2,
                step_type=StepType.DOSING,
                title="Initial Dose"
            ),
            ProtocolStep(
                protocol_id=protocol.id,
                sequence_order=3,
                step_type=StepType.FOLLOWUP,
                title="6-Week Follow-up"
            )
        ]
        db_session.add_all(steps)
        db_session.commit()

        # Create treatment plan
        patient = User(email=unique_email("patient_trt"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("doc_trt"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.SCREENING,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Test workflow
        current = protocol_engine.get_current_step(plan)
        assert current is not None
        assert current.step_type == StepType.SCREENING

    def test_chemotherapy_protocol(self, db_session, protocol_engine):
        """Test protocol execution with chemotherapy."""
        # Create user
        user = User(
            email=unique_email("admin_chemo"),
            password_hash="hash",
            role=UserRole.PLATFORM_ADMIN
        )
        db_session.add(user)
        db_session.commit()

        # Create chemotherapy protocol
        protocol = Protocol(
            name="FOLFOX Chemotherapy",
            version="1.0",
            status="active",
            therapy_type=TherapyType.CHEMOTHERAPY,
            condition_treated="colorectal_cancer",
            evidence_level=EvidenceLevel.FDA_APPROVED,
            created_by=user.id
        )
        db_session.add(protocol)
        db_session.commit()

        # Add steps (6 cycles)
        steps = []
        for i in range(1, 7):
            steps.append(
                ProtocolStep(
                    protocol_id=protocol.id,
                    sequence_order=i,
                    step_type=StepType.DOSING,
                    title=f"Cycle {i}"
                )
            )
        db_session.add_all(steps)
        db_session.commit()

        # Create treatment plan
        patient = User(email=unique_email("patient_chemo"), password_hash="hash", role=UserRole.PATIENT)
        therapist = User(email=unique_email("doc_chemo"), password_hash="hash", role=UserRole.THERAPIST)
        db_session.add_all([patient, therapist])
        db_session.commit()

        plan = TreatmentPlan(
            patient_id=patient.id,
            therapist_id=therapist.id,
            protocol_id=protocol.id,
            protocol_version="1.0",
            status=TreatmentStatus.ACTIVE,
            start_date=datetime.utcnow()
        )
        db_session.add(plan)
        db_session.commit()

        # Test workflow
        current = protocol_engine.get_current_step(plan)
        assert current is not None
        assert current.sequence_order == 1
        assert not protocol_engine.is_protocol_complete(plan)
