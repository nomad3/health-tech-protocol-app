#!/usr/bin/env python3
"""
Database Seeding Script for PsyProtocol Platform

This script populates the database with comprehensive demo data including:
- Demo users (admin, director, therapists, patients)
- Demo clinic with therapist profiles
- Patient profiles with medical history
- All 8 example protocols from JSON files
- Sample treatment plans and sessions

Usage:
    python seed_database.py

Requirements:
    - Database must exist and migrations must be run
    - Run from backend directory: cd backend && python seed_database.py
    - Or use the convenience script: ./scripts/reset_and_seed.sh

The script is idempotent - it checks for existing data and skips creation if found.
Safe to run multiple times.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import (
    Base,
    User,
    UserRole,
    Clinic,
    TherapistProfile,
    PatientProfile,
    Protocol,
    ProtocolStep,
    SafetyCheck,
    TherapyType,
    EvidenceLevel,
    StepType,
    TreatmentPlan,
    TreatmentSession,
    SessionDocumentation,
    TreatmentStatus,
    SessionStatus,
)
from app.core.security import hash_password


# Demo user credentials
DEMO_USERS = [
    {
        "email": "admin@psyprotocol.com",
        "password": "Admin123!",
        "role": UserRole.PLATFORM_ADMIN,
    },
    {
        "email": "director@psyprotocol.com",
        "password": "Director123!",
        "role": UserRole.MEDICAL_DIRECTOR,
    },
    {
        "email": "therapist1@psyprotocol.com",
        "password": "Therapist123!",
        "role": UserRole.THERAPIST,
    },
    {
        "email": "therapist2@psyprotocol.com",
        "password": "Therapist123!",
        "role": UserRole.THERAPIST,
    },
    {
        "email": "patient1@psyprotocol.com",
        "password": "Patient123!",
        "role": UserRole.PATIENT,
    },
    {
        "email": "patient2@psyprotocol.com",
        "password": "Patient123!",
        "role": UserRole.PATIENT,
    },
]

# Protocol JSON files to load
PROTOCOL_FILES = [
    "psilocybin_depression_detailed_protocol.json",
    "mdma_ptsd_maps_protocol.json",
    "ketamine_depression_protocol.json",
    "lsd_microdosing_protocol.json",
    "testosterone_optimization_protocol.json",
    "testosterone_replacement_protocol.json",
    "chemotherapy_protocol.json",
    "stem_cell_therapy_protocol.json",
]


def create_demo_users(db: Session) -> dict:
    """Create demo users and return them by email."""
    print("\n=== Creating Demo Users ===")
    users = {}

    for user_data in DEMO_USERS:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()

        if existing_user:
            print(f"  ✓ User {user_data['email']} already exists (ID: {existing_user.id})")
            users[user_data["email"]] = existing_user
        else:
            new_user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True,
            )
            db.add(new_user)
            db.flush()
            users[user_data["email"]] = new_user
            print(f"  + Created user {user_data['email']} (ID: {new_user.id}, Role: {user_data['role'].value})")

    db.commit()
    return users


def create_demo_clinic(db: Session) -> Clinic:
    """Create demo clinic."""
    print("\n=== Creating Demo Clinic ===")

    existing_clinic = db.query(Clinic).filter(
        Clinic.name == "Center for Evidence-Based Therapies"
    ).first()

    if existing_clinic:
        print(f"  ✓ Clinic already exists (ID: {existing_clinic.id})")
        return existing_clinic

    clinic = Clinic(
        name="Center for Evidence-Based Therapies",
        type="clinic",
        address="123 Wellness St, San Francisco, CA 94102",
        license_numbers=["CA-MED-12345", "DEA-XY9876543"],
        certifications=[
            "MAPS Certification for MDMA-Assisted Therapy",
            "Johns Hopkins Psilocybin Research Certification",
            "State Schedule I Research License",
            "CLIA Laboratory Certification",
        ],
        protocols_enabled=[
            "psilocybin",
            "mdma",
            "ketamine",
            "lsd",
            "testosterone",
            "chemotherapy",
            "stem_cell",
        ],
    )

    db.add(clinic)
    db.commit()
    print(f"  + Created clinic: {clinic.name} (ID: {clinic.id})")
    return clinic


def create_therapist_profiles(db: Session, users: dict, clinic: Clinic) -> dict:
    """Create therapist profiles for therapist users."""
    print("\n=== Creating Therapist Profiles ===")
    therapist_profiles = {}

    therapist_data = [
        {
            "email": "therapist1@psyprotocol.com",
            "license_type": "MD",
            "license_number": "CA-MD-98765",
            "license_state": "CA",
            "specialties": ["Psychiatry", "Psychedelic-Assisted Therapy", "Trauma Treatment"],
            "certifications": [
                "Board Certified in Psychiatry",
                "MAPS MDMA Therapy Training",
                "Johns Hopkins Psilocybin Facilitator Training",
            ],
            "protocols_certified": [
                "psilocybin",
                "mdma",
                "ketamine",
                "lsd",
            ],
        },
        {
            "email": "therapist2@psyprotocol.com",
            "license_type": "PhD",
            "license_number": "CA-PSY-54321",
            "license_state": "CA",
            "specialties": ["Clinical Psychology", "Depression Treatment", "Psychotherapy"],
            "certifications": [
                "Licensed Clinical Psychologist",
                "Ketamine-Assisted Psychotherapy Certification",
                "CAPS-5 Rater Certification",
            ],
            "protocols_certified": [
                "psilocybin",
                "ketamine",
            ],
        },
    ]

    for data in therapist_data:
        user = users.get(data["email"])
        if not user:
            continue

        existing_profile = db.query(TherapistProfile).filter(
            TherapistProfile.user_id == user.id
        ).first()

        if existing_profile:
            print(f"  ✓ Profile for {data['email']} already exists (ID: {existing_profile.id})")
            therapist_profiles[data["email"]] = existing_profile
        else:
            profile = TherapistProfile(
                user_id=user.id,
                clinic_id=clinic.id,
                license_type=data["license_type"],
                license_number=data["license_number"],
                license_state=data["license_state"],
                specialties=data["specialties"],
                certifications=data["certifications"],
                protocols_certified=data["protocols_certified"],
            )
            db.add(profile)
            db.flush()
            therapist_profiles[data["email"]] = profile
            print(f"  + Created therapist profile for {data['email']} ({data['license_type']}, ID: {profile.id})")

    db.commit()
    return therapist_profiles


def create_patient_profiles(db: Session, users: dict) -> dict:
    """Create patient profiles for patient users."""
    print("\n=== Creating Patient Profiles ===")
    patient_profiles = {}

    patient_data = [
        {
            "email": "patient1@psyprotocol.com",
            "date_of_birth": datetime(1985, 6, 15).date(),
            "medical_history": {
                "diagnoses": [
                    "Major Depressive Disorder (Treatment-Resistant)",
                    "Generalized Anxiety Disorder",
                ],
                "past_treatments": [
                    "SSRIs (Sertraline, Escitalopram) - partial response",
                    "SNRIs (Venlafaxine) - minimal response",
                    "Cognitive Behavioral Therapy - ongoing",
                ],
                "allergies": ["Penicillin"],
                "surgical_history": ["Appendectomy (2010)"],
            },
            "medications": [
                {"name": "Escitalopram", "dose": "20mg", "frequency": "daily"},
                {"name": "Lorazepam", "dose": "0.5mg", "frequency": "as needed"},
            ],
            "contraindications": [],
        },
        {
            "email": "patient2@psyprotocol.com",
            "date_of_birth": datetime(1992, 3, 22).date(),
            "medical_history": {
                "diagnoses": [
                    "Post-Traumatic Stress Disorder",
                    "Depression",
                ],
                "past_treatments": [
                    "Prolonged Exposure Therapy - partial response",
                    "EMDR - incomplete",
                    "Sertraline - discontinued due to side effects",
                ],
                "allergies": [],
                "surgical_history": [],
            },
            "medications": [
                {"name": "Prazosin", "dose": "2mg", "frequency": "bedtime"},
            ],
            "contraindications": [],
        },
    ]

    for data in patient_data:
        user = users.get(data["email"])
        if not user:
            continue

        existing_profile = db.query(PatientProfile).filter(
            PatientProfile.user_id == user.id
        ).first()

        if existing_profile:
            print(f"  ✓ Profile for {data['email']} already exists (ID: {existing_profile.id})")
            patient_profiles[data["email"]] = existing_profile
        else:
            profile = PatientProfile(
                user_id=user.id,
                date_of_birth=data["date_of_birth"],
                medical_history=data["medical_history"],
                medications=data["medications"],
                contraindications=data["contraindications"],
            )
            db.add(profile)
            db.flush()
            patient_profiles[data["email"]] = profile
            age = (datetime.now().date() - data["date_of_birth"]).days // 365
            print(f"  + Created patient profile for {data['email']} (Age: {age}, ID: {profile.id})")

    db.commit()
    return patient_profiles


def map_therapy_type(therapy_type_str: str) -> TherapyType:
    """Map protocol JSON therapy_type string to TherapyType enum."""
    mapping = {
        "psilocybin_psychedelic": TherapyType.PSILOCYBIN,
        "psilocybin": TherapyType.PSILOCYBIN,
        "mdma_psychedelic": TherapyType.MDMA,
        "mdma": TherapyType.MDMA,
        "ketamine": TherapyType.KETAMINE,
        "ketamine_psychedelic": TherapyType.KETAMINE,
        "lsd": TherapyType.LSD,
        "lsd_microdosing": TherapyType.LSD,
        "testosterone": TherapyType.TESTOSTERONE,
        "testosterone_replacement": TherapyType.TESTOSTERONE,
        "chemotherapy": TherapyType.CHEMOTHERAPY,
        "stem_cell": TherapyType.STEM_CELL,
        "stem_cell_therapy": TherapyType.STEM_CELL,
    }
    return mapping.get(therapy_type_str.lower(), TherapyType.OTHER)


def map_evidence_level(evidence_level_str: str) -> EvidenceLevel:
    """Map protocol JSON evidence_level string to EvidenceLevel enum."""
    mapping = {
        "fda_approved": EvidenceLevel.FDA_APPROVED,
        "phase_3_clinical_trial": EvidenceLevel.PHASE_3,
        "phase_3_trial": EvidenceLevel.PHASE_3,
        "phase_3_clinical_trial_fda_approved": EvidenceLevel.FDA_APPROVED,
        "phase_2_clinical_trial": EvidenceLevel.PHASE_2,
        "phase_2_trial": EvidenceLevel.PHASE_2,
        "phase_1_clinical_trial": EvidenceLevel.PHASE_1,
        "phase_1_trial": EvidenceLevel.PHASE_1,
        "preclinical": EvidenceLevel.PRECLINICAL,
        "clinical_practice": EvidenceLevel.CLINICAL_PRACTICE,
    }
    return mapping.get(evidence_level_str.lower(), EvidenceLevel.CLINICAL_PRACTICE)


def map_step_type(step_type_str: str) -> StepType:
    """Map protocol JSON step_type string to StepType enum."""
    mapping = {
        "screening": StepType.SCREENING,
        "preparation": StepType.PREPARATION,
        "dosing": StepType.DOSING,
        "intervention": StepType.DOSING,  # 'intervention' in JSON maps to dosing
        "integration": StepType.INTEGRATION,
        "decision_point": StepType.DECISION_POINT,
        "followup": StepType.FOLLOWUP,
    }
    return mapping.get(step_type_str.lower(), StepType.FOLLOWUP)


def load_protocols_from_json(db: Session, admin_user: User) -> list:
    """Load all protocol JSON files and create Protocol records."""
    print("\n=== Loading Protocols from JSON Files ===")
    protocols = []
    examples_dir = Path(__file__).parent / "examples"

    for filename in PROTOCOL_FILES:
        filepath = examples_dir / filename

        if not filepath.exists():
            print(f"  ⚠ Warning: File not found: {filename}")
            continue

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            protocol_data = data.get("protocol", {})
            steps_data = data.get("steps", [])

            # Check if protocol already exists
            existing_protocol = db.query(Protocol).filter(
                Protocol.name == protocol_data["name"],
                Protocol.version == protocol_data["version"],
            ).first()

            if existing_protocol:
                print(f"  ✓ Protocol '{protocol_data['name']}' already exists (ID: {existing_protocol.id})")
                protocols.append(existing_protocol)
                continue

            # Create protocol
            protocol = Protocol(
                name=protocol_data["name"],
                version=protocol_data["version"],
                status="active",  # Set to active so it appears in protocol browser
                therapy_type=map_therapy_type(protocol_data["therapy_type"]),
                condition_treated=protocol_data["condition_treated"],
                evidence_level=map_evidence_level(protocol_data["evidence_level"]),
                overview=protocol_data.get("overview", ""),
                duration_weeks=protocol_data.get("duration_weeks"),
                total_sessions=protocol_data.get("total_sessions"),
                evidence_sources=protocol_data.get("evidence_sources", []),
                created_by=admin_user.id,
            )

            db.add(protocol)
            db.flush()

            # Create protocol steps
            steps_created = 0
            for step_data in steps_data:
                step = ProtocolStep(
                    protocol_id=protocol.id,
                    sequence_order=step_data["sequence_order"],
                    step_type=map_step_type(step_data["step_type"]),
                    title=step_data["title"],
                    description=step_data.get("description", ""),
                    duration_minutes=step_data.get("duration_minutes"),
                    required_roles=step_data.get("required_roles", []),
                    evaluation_rules=step_data.get("evaluation_rules"),
                    branch_outcomes=step_data.get("branch_outcomes"),
                    clinical_scales=step_data.get("clinical_scales", []),
                    vitals_monitoring=step_data.get("vitals_monitoring"),
                )

                db.add(step)
                db.flush()
                steps_created += 1

                # Create safety checks if present (nested in evaluation_rules)
                evaluation_rules = step_data.get("evaluation_rules", {})
                if evaluation_rules and "absolute_contraindications" in evaluation_rules:
                    for contraindication in evaluation_rules["absolute_contraindications"]:
                        safety_check = SafetyCheck(
                            protocol_step_id=step.id,
                            check_type="absolute_contraindication",
                            condition=contraindication,
                            severity="blocking",
                            override_allowed="false",
                        )
                        db.add(safety_check)

            db.commit()
            protocols.append(protocol)
            print(f"  + Created protocol '{protocol.name}' with {steps_created} steps (ID: {protocol.id})")

        except Exception as e:
            print(f"  ✗ Error loading {filename}: {str(e)}")
            db.rollback()
            continue

    return protocols


def create_sample_treatment_plans(
    db: Session,
    users: dict,
    protocols: list,
    clinic: Clinic,
) -> list:
    """Create sample treatment plans linking patients, therapists, and protocols."""
    print("\n=== Creating Sample Treatment Plans ===")
    treatment_plans = []

    if not protocols:
        print("  ⚠ No protocols available, skipping treatment plans")
        return treatment_plans

    # Find patient and therapist users
    patient1 = users.get("patient1@psyprotocol.com")
    patient2 = users.get("patient2@psyprotocol.com")
    therapist1 = users.get("therapist1@psyprotocol.com")
    therapist2 = users.get("therapist2@psyprotocol.com")

    if not all([patient1, patient2, therapist1, therapist2]):
        print("  ⚠ Missing required users, skipping treatment plans")
        return treatment_plans

    # Find specific protocols
    psilocybin_protocol = next(
        (p for p in protocols if "psilocybin" in p.name.lower() and "depression" in p.name.lower()),
        None
    )
    mdma_protocol = next(
        (p for p in protocols if "mdma" in p.name.lower()),
        None
    )

    plan_data = []

    if psilocybin_protocol:
        plan_data.append({
            "patient": patient1,
            "therapist": therapist1,
            "protocol": psilocybin_protocol,
            "status": TreatmentStatus.ACTIVE,
            "start_date": datetime.utcnow() - timedelta(weeks=2),
            "customizations": {
                "dose_mg": 25,
                "preparation_sessions": 3,
                "notes": "Patient responding well to initial preparation sessions",
            },
        })

    if mdma_protocol:
        plan_data.append({
            "patient": patient2,
            "therapist": therapist1,
            "protocol": mdma_protocol,
            "status": TreatmentStatus.SCREENING,
            "start_date": datetime.utcnow() - timedelta(days=5),
            "customizations": {
                "dose_mg": 120,
                "notes": "Completing CAPS-5 assessment and medical screening",
            },
        })

    # Add a completed plan if we have a third protocol
    if len(protocols) >= 3:
        plan_data.append({
            "patient": patient1,
            "therapist": therapist2,
            "protocol": protocols[2],
            "status": TreatmentStatus.COMPLETED,
            "start_date": datetime.utcnow() - timedelta(weeks=16),
            "customizations": {
                "notes": "Successfully completed protocol with significant improvement",
            },
        })

    for data in plan_data:
        # Check if plan already exists
        existing_plan = db.query(TreatmentPlan).filter(
            TreatmentPlan.patient_id == data["patient"].id,
            TreatmentPlan.protocol_id == data["protocol"].id,
        ).first()

        if existing_plan:
            print(f"  ✓ Plan for {data['patient'].email} + {data['protocol'].name} already exists")
            treatment_plans.append(existing_plan)
            continue

        plan = TreatmentPlan(
            patient_id=data["patient"].id,
            therapist_id=data["therapist"].id,
            clinic_id=clinic.id,
            protocol_id=data["protocol"].id,
            protocol_version=data["protocol"].version,
            status=data["status"],
            start_date=data["start_date"],
            estimated_completion=data["start_date"] + timedelta(weeks=data["protocol"].duration_weeks or 12),
            customizations=data["customizations"],
        )

        db.add(plan)
        db.flush()
        treatment_plans.append(plan)
        print(f"  + Created treatment plan: {data['patient'].email} → {data['protocol'].name} (Status: {data['status'].value}, ID: {plan.id})")

    db.commit()
    return treatment_plans


def create_sample_sessions(
    db: Session,
    treatment_plans: list,
) -> list:
    """Create sample treatment sessions for treatment plans."""
    print("\n=== Creating Sample Treatment Sessions ===")
    sessions = []

    if not treatment_plans:
        print("  ⚠ No treatment plans available, skipping sessions")
        return sessions

    for plan in treatment_plans:
        # Get protocol steps
        protocol_steps = db.query(ProtocolStep).filter(
            ProtocolStep.protocol_id == plan.protocol_id
        ).order_by(ProtocolStep.sequence_order).limit(3).all()

        if not protocol_steps:
            continue

        # Create sessions based on plan status
        if plan.status == TreatmentStatus.ACTIVE:
            # Create 2 completed sessions and 1 scheduled
            for i, step in enumerate(protocol_steps[:2]):
                session_date = plan.start_date + timedelta(days=i * 7)
                session = TreatmentSession(
                    treatment_plan_id=plan.id,
                    protocol_step_id=step.id,
                    scheduled_at=session_date,
                    actual_start=session_date,
                    actual_end=session_date + timedelta(minutes=step.duration_minutes or 60),
                    therapist_id=plan.therapist_id,
                    location="in_person",
                    status=SessionStatus.COMPLETED,
                )
                db.add(session)
                db.flush()

                # Add documentation for completed session
                if i == 1:  # Add detailed documentation for second session
                    documentation = SessionDocumentation(
                        treatment_session_id=session.id,
                        vitals=[
                            {"time": "T+0", "bp": "120/80", "hr": 72, "temp": 98.6, "spo2": 98},
                            {"time": "T+30", "bp": "118/78", "hr": 70, "temp": 98.4, "spo2": 99},
                        ],
                        clinical_scales={"PHQ-9": 14, "GAD-7": 8},
                        therapist_notes="Patient engaged well in preparation session. Discussed intentions and expectations for upcoming dosing session.",
                        patient_subjective_notes="Feeling nervous but hopeful about treatment.",
                    )
                    db.add(documentation)

                sessions.append(session)

            # Add upcoming scheduled session
            if len(protocol_steps) > 2:
                next_session = TreatmentSession(
                    treatment_plan_id=plan.id,
                    protocol_step_id=protocol_steps[2].id,
                    scheduled_at=datetime.utcnow() + timedelta(days=3),
                    therapist_id=plan.therapist_id,
                    location="in_person",
                    status=SessionStatus.SCHEDULED,
                )
                db.add(next_session)
                sessions.append(next_session)

        elif plan.status == TreatmentStatus.SCREENING and protocol_steps:
            # Create 1 completed screening session
            session_date = plan.start_date + timedelta(days=1)
            session = TreatmentSession(
                treatment_plan_id=plan.id,
                protocol_step_id=protocol_steps[0].id,
                scheduled_at=session_date,
                actual_start=session_date,
                actual_end=session_date + timedelta(minutes=protocol_steps[0].duration_minutes or 60),
                therapist_id=plan.therapist_id,
                location="in_person",
                status=SessionStatus.COMPLETED,
            )
            db.add(session)
            sessions.append(session)

        elif plan.status == TreatmentStatus.COMPLETED:
            # Create a final follow-up session
            if protocol_steps:
                session_date = plan.start_date + timedelta(weeks=12)
                session = TreatmentSession(
                    treatment_plan_id=plan.id,
                    protocol_step_id=protocol_steps[-1].id,
                    scheduled_at=session_date,
                    actual_start=session_date,
                    actual_end=session_date + timedelta(minutes=60),
                    therapist_id=plan.therapist_id,
                    location="in_person",
                    status=SessionStatus.COMPLETED,
                )
                db.add(session)
                db.flush()

                # Add completion documentation
                documentation = SessionDocumentation(
                    treatment_session_id=session.id,
                    clinical_scales={"PHQ-9": 4, "GAD-7": 3, "improvement": "70%"},
                    therapist_notes="Patient has shown significant improvement. Depression symptoms reduced by 70%. Excellent progress in integration work.",
                    patient_subjective_notes="Feel like a different person. The treatment has been life-changing.",
                )
                db.add(documentation)
                sessions.append(session)

    db.commit()
    print(f"  + Created {len(sessions)} treatment sessions")
    return sessions


def main():
    """Main seeding function."""
    print("=" * 70)
    print("PsyProtocol Database Seeding Script")
    print("=" * 70)

    # Create database session
    db = SessionLocal()

    try:
        # Step 1: Create demo users
        users = create_demo_users(db)

        # Step 2: Create demo clinic
        clinic = create_demo_clinic(db)

        # Step 3: Create therapist profiles
        therapist_profiles = create_therapist_profiles(db, users, clinic)

        # Step 4: Create patient profiles
        patient_profiles = create_patient_profiles(db, users)

        # Step 5: Load protocols from JSON files
        admin_user = users.get("admin@psyprotocol.com")
        protocols = load_protocols_from_json(db, admin_user)

        # Step 6: Create sample treatment plans
        treatment_plans = create_sample_treatment_plans(db, users, protocols, clinic)

        # Step 7: Create sample sessions
        sessions = create_sample_sessions(db, treatment_plans)

        print("\n" + "=" * 70)
        print("✓ Database seeding completed successfully!")
        print("=" * 70)
        print(f"\nSummary:")
        print(f"  - Users created: {len(users)}")
        print(f"  - Clinics created: 1")
        print(f"  - Therapist profiles: {len(therapist_profiles)}")
        print(f"  - Patient profiles: {len(patient_profiles)}")
        print(f"  - Protocols loaded: {len(protocols)}")
        print(f"  - Treatment plans: {len(treatment_plans)}")
        print(f"  - Treatment sessions: {len(sessions)}")
        print(f"\nDemo Login Credentials:")
        print(f"  Admin:     admin@psyprotocol.com / Admin123!")
        print(f"  Director:  director@psyprotocol.com / Director123!")
        print(f"  Therapist: therapist1@psyprotocol.com / Therapist123!")
        print(f"  Patient:   patient1@psyprotocol.com / Patient123!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
