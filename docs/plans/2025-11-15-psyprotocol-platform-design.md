# PsyProtocol Platform - Complete Design Document

**Date:** 2025-11-15
**Version:** 1.0
**Status:** Approved for Implementation

---

## Executive Summary

**PsyProtocol** is an AI-powered protocol engine and patient journey platform for psychedelic-assisted therapy. It connects patients with therapists/clinics, guides them through evidence-based treatment protocols with dynamic branching, and ensures safety through tiered contraindication checking and comprehensive session documentation.

**Target Market:** Psychedelic therapy clinics (psilocybin, MDMA, ketamine)
**MVP Timeline:** 2-3 months with small team
**Tech Stack:** Python/FastAPI backend, React/TypeScript frontend, PostgreSQL, Redis, Claude AI
**Deployment:** Single GCP VM with Docker Compose (simplified for MVP)

---

## 1. Platform Overview & Architecture

### Product Vision

**What it is:**
An AI-powered protocol engine and patient journey platform for psychedelic-assisted therapy. Connects patients with therapists/clinics, guides them through evidence-based treatment protocols with dynamic branching, and ensures safety through tiered contraindication checking and comprehensive session documentation.

### Core Value Propositions

**For Patients:**
- Discover safe, evidence-based psychedelic therapy
- Understand what to expect through AI-generated guides
- Get matched with qualified providers
- Track treatment progress

**For Therapists/Clinics:**
- Deploy validated protocols instantly
- Dynamic decision support during treatment
- Reduce documentation burden
- Ensure compliance automatically

**For the Field:**
- Standardize best practices
- Capture outcomes data
- Accelerate evidence generation

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Patient    │  Therapist   │   Clinic     │   Admin    │
│   Portal     │  Dashboard   │   Admin      │   Panel    │
└──────────────┴──────────────┴──────────────┴────────────┘
                           │
                    REST API (FastAPI)
                           │
├──────────────┬────────────────┬──────────────┬───────────┤
│   Protocol   │   Patient      │   Safety     │    AI     │
│   Engine     │   Journey      │   System     │   Layer   │
└──────────────┴────────────────┴──────────────┴───────────┘
                           │
                  PostgreSQL + Redis
                           │
            ┌───────────────┴───────────────┐
            │                               │
     Anthropic Claude API          Stripe Payments
```

### Tech Stack

- **Backend:** Python 3.11+ with FastAPI
- **Database:** PostgreSQL 15+ (relational protocol data, audit logs)
- **Cache:** Redis (session state, real-time vitals)
- **Frontend:** React 18 + TypeScript + Tailwind CSS
- **AI:** Anthropic Claude API (Sonnet for speed, Opus for protocol extraction)
- **Payments:** Stripe
- **Auth:** JWT with refresh tokens
- **Deployment:** Docker + Docker Compose on GCP VM

---

## 2. Core Data Model

### Key Entities & Relationships

#### 1. Protocols (The Heart of the System)

```python
Protocol:
  - id, name, version, status (draft/active/archived)
  - therapy_type (psilocybin, MDMA, ketamine, etc.)
  - condition_treated (depression, PTSD, anxiety, etc.)
  - evidence_level (FDA-approved, Phase 3, Phase 2, etc.)
  - created_by (admin user)
  - created_at, updated_at
  - evidence_sources[] (linked research papers)

ProtocolStep:
  - id, protocol_id, sequence_order
  - step_type (screening, preparation, dosing, integration, decision_point)
  - title, description, duration_minutes
  - required_roles (therapist, medical_supervisor, etc.)
  - documentation_template_id

DecisionPoint (extends ProtocolStep):
  - evaluation_rules (JSON: conditions to evaluate)
  - branch_outcomes[] (possible next steps based on evaluation)

SafetyCheck:
  - id, protocol_step_id
  - check_type (absolute_contraindication, relative_contraindication, risk_factor)
  - condition (medication, diagnosis, lab_value, etc.)
  - severity (blocking, warning, info)
  - evidence_source
```

#### 2. Users & Organizations

```python
User:
  - id, email, password_hash, role (patient, therapist, clinic_admin, platform_admin)
  - profile_id (polymorphic: PatientProfile or TherapistProfile)

Clinic:
  - id, name, type (clinic, solo_practice)
  - address, license_numbers[], certifications[]
  - protocols_enabled[] (which protocols this clinic offers)

TherapistProfile:
  - user_id, clinic_id (nullable for solo practitioners)
  - license_type, license_number, license_state
  - specialties[], certifications[]
  - protocols_certified[] (which protocols they can deliver)

PatientProfile:
  - user_id, date_of_birth
  - medical_history (JSON)
  - medications[] (current medications)
  - contraindications[] (detected from screening)
```

#### 3. Patient Journey

```python
TreatmentPlan:
  - id, patient_id, therapist_id, clinic_id
  - protocol_id, protocol_version
  - status (screening, active, paused, completed)
  - start_date, estimated_completion
  - customizations (JSON: any protocol modifications)

TreatmentSession:
  - id, treatment_plan_id, protocol_step_id
  - scheduled_at, actual_start, actual_end
  - therapist_id, location (in_person/telehealth)
  - status (scheduled, in_progress, completed, cancelled)

SessionDocumentation:
  - id, treatment_session_id
  - vitals[] (timestamped BP, HR, temp, SpO2 readings)
  - clinical_scales (PHQ-9, GAD-7, MEQ30, etc.)
  - therapist_notes, patient_subjective_notes
  - adverse_events[]
  - decision_point_evaluations[] (which branches were taken and why)
```

#### 4. Safety & Compliance

```python
ContraindicationCheck:
  - id, patient_id, treatment_plan_id
  - check_date, checked_by (therapist_id)
  - contraindications_found[]
  - risk_score (0-100)
  - override_reason (if therapist proceeded despite warning)

AuditLog:
  - id, user_id, action, resource_type, resource_id
  - timestamp, ip_address
  - changes (JSON diff for data modifications)
```

---

## 3. Protocol Engine - Dynamic Branching

### How Protocols Execute with Decision Points

**Protocol Execution Flow:**

1. Patient starts treatment plan → Creates TreatmentPlan linked to specific Protocol version
2. System traverses ProtocolSteps sequentially → Each step has sequence_order
3. When reaching DecisionPoint step → Evaluate rules against patient data
4. Rules determine next step → Branch to different paths based on evaluation
5. Continue until protocol complete → All required steps marked done

### Decision Point Rule Engine

**Example: Dose Determination**

```json
{
  "step_id": "dose-determination",
  "title": "Determine Psilocybin Dosage",
  "evaluation_rules": {
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
      "high_weight + low_anxiety": "dosage_30mg"
    }
  },
  "branch_outcomes": [
    {
      "outcome_id": "dosage_15mg",
      "next_step_id": "dosing_session_15mg",
      "rationale": "Lower dose recommended due to body weight and anxiety level"
    }
  ]
}
```

### Safety Check Evaluation

**Absolute Contraindication (Blocking):**

```json
{
  "check_type": "absolute_contraindication",
  "condition": {
    "type": "diagnosis",
    "icd10_codes": ["F20.*"],
    "description": "Active psychotic disorder"
  },
  "severity": "blocking",
  "action": "prevent_progression",
  "override_allowed": false,
  "evidence_source": "PMID:32234234"
}
```

**Relative Contraindication (Warning):**

```json
{
  "check_type": "relative_contraindication",
  "condition": {
    "type": "medication",
    "medication_classes": ["SSRI", "SNRI"],
    "description": "Currently taking serotonergic medication"
  },
  "severity": "warning",
  "action": "require_documentation",
  "override_allowed": true,
  "override_requirements": ["psychiatrist_approval", "tapering_plan"],
  "evidence_source": "PMID:33445566"
}
```

### Therapist Override Workflow

- **Soft warnings** → Therapist acknowledges + documents reasoning
- **Hard blocks** → Requires medical director approval + detailed justification
- **All overrides** logged in AuditLog with full context

---

## 4. AI Layer - Claude Integration

### Three AI Features Across the Platform

#### 1. Protocol Assistant (Admin Tool)

**Purpose:** Help platform admins rapidly create protocols from research papers.

**Workflow:**
```
Admin uploads PDF → Claude extracts protocol structure →
Admin reviews/edits → Publishes to protocol library
```

**Implementation:**

```python
# API Endpoint: POST /api/admin/protocols/extract

Input:
- PDF file (research paper, clinical trial protocol)
- Therapy type hint (psilocybin, MDMA, etc.)
- Target condition (depression, PTSD, etc.)

Claude Prompt:
"""
You are a clinical protocol extraction expert. Analyze this research paper
and extract a structured treatment protocol.

Extract:
1. Protocol steps (screening, preparation, dosing, integration phases)
2. Dosing schedules (mg/kg, timing, frequency)
3. Contraindications (absolute and relative)
4. Safety monitoring requirements
5. Clinical scales used (PHQ-9, CAPS-5, etc.)
6. Decision points (when to adjust dose, add sessions, etc.)
7. Evidence sources for each recommendation

Return structured JSON matching our ProtocolStep schema.
"""

Output:
- Structured protocol JSON
- Evidence tags linking each step to paper sections
- Suggested safety checks
```

#### 2. Patient Education Generator (Patient Tool)

**Purpose:** Create personalized, accessible explanations of protocols and treatment phases.

**Workflow:**
```
Patient views protocol → Requests "What to expect" →
Claude generates personalized explanation → Patient reads prep materials
```

**Implementation:**

```python
# API Endpoint: GET /api/patients/protocols/{id}/explanation

Claude Prompt:
"""
You are a compassionate psychedelic therapy educator. Create a warm,
clear explanation of this treatment protocol for a patient.

Protocol: {protocol_name} for {condition}
Patient context: {demographics, concerns}

Generate:
1. Overview (2-3 paragraphs, compassionate tone)
2. What to expect in each phase (preparation, dosing day, integration)
3. Common experiences during dosing session
4. Safety measures in place
5. How to prepare mentally/physically
6. FAQ addressing common concerns

Tone: Reassuring, evidence-based, non-technical language.
"""

Output:
- Personalized preparation guide
- Phase-by-phase expectations
- Safety reassurance
```

#### 3. Clinical Decision Support (Therapist Tool)

**Purpose:** Real-time suggestions during treatment based on patient data and protocol context.

**Workflow:**
```
Therapist enters session data → AI analyzes patterns →
Suggests evidence-based interventions → Therapist decides whether to follow
```

**Implementation:**

```python
# API Endpoint: POST /api/therapist/decision-support

Claude Prompt:
"""
You are a clinical decision support system for psychedelic-assisted therapy.

Current situation:
- Session: {session_type} at T+{minutes_elapsed}
- Vitals: BP {bp}, HR {hr}, Patient state: {observed_state}
- Patient history: {previous_sessions_summary}
- Protocol expectations: {expected_range_for_this_phase}

Analyze:
1. Are vitals within expected range?
2. Is patient experience typical for this phase?
3. Are there any safety concerns?
4. Should therapist intervene or adjust?

Provide:
- Risk level (low/moderate/high)
- Specific recommendations if applicable
- Evidence basis for suggestion
- When to escalate to medical supervisor

Be conservative. Flag anything borderline.
"""

Output:
- Risk assessment
- Suggested actions (if any)
- Evidence references
```

### AI Safety & Compliance

- All AI suggestions logged in AuditLog
- AI never makes autonomous decisions (human-in-the-loop)
- Clinical decision support labeled as "AI suggestion - clinical judgment required"
- Model: Claude Sonnet for speed, Opus for protocol extraction accuracy
- Rate limiting + fallback handling if API unavailable

---

## 5. User Journeys & Core Workflows

### Patient Journey (End-to-End)

**Phase 1: Discovery & Matching**

1. Patient lands on platform
2. Browse protocol library (psilocybin for depression, MDMA for PTSD, etc.)
   - AI-generated plain-language explanations
   - Evidence level badges (FDA Phase 3, etc.)
   - Expected timeline, session count, cost range
3. Select protocol of interest
4. Pre-screening quiz (10-15 questions)
   - Mental health history
   - Current medications
   - Key contraindications
5. AI risk assessment
   - Green: "You may be a good candidate"
   - Yellow: "Some considerations - discuss with provider"
   - Red: "This protocol may not be safe - consult psychiatrist"
6. Search for providers
   - Filter: Location, telehealth, insurance, availability
   - Clinic vs. solo practitioner
   - Provider profiles (certifications, approach, reviews)
7. Request consultation with provider

**Phase 2: Screening & Onboarding**

8. Initial consultation (video/in-person)
   - Therapist reviews full medical history
   - Platform runs formal contraindication checks
   - Risk score calculated
9. If approved → Create TreatmentPlan
   - Protocol assigned
   - Custom adjustments noted
   - Payment/insurance setup
10. Patient reviews informed consent
    - AI-generated personalized consent form
    - Protocol risks/benefits for their specific case
    - Digital signature

**Phase 3: Treatment Delivery**

11. Preparation sessions (1-3 sessions)
    - Patient portal shows: "What to expect today"
    - Therapist uses structured documentation template
    - Baseline clinical scales (PHQ-9, etc.)
12. Pre-dosing safety check
    - System verifies contraindication screen is current
    - Confirms medical supervisor available (if required)
    - Therapist completes pre-session checklist
13. Dosing session
    - Decision point: AI + therapist determine dose
    - Real-time vitals logging (manual entry every 30min)
    - Session timeline tracker (onset, peak, integration phases)
    - AI decision support monitors for safety concerns
    - Rich documentation (therapist observations, patient experience)
14. Integration sessions (3-6 sessions over weeks/months)
    - Patient reflects on experience
    - Clinical scales tracked (measure improvement)
    - Decision point: Additional sessions needed?
15. Protocol completion
    - Final outcome measures
    - Patient feedback
    - Therapist summary

### Therapist Workflow (Daily Use)

**Dashboard View:**
```
Today's Schedule:
- 9:00 AM - Sarah K. (Preparation Session 2)
- 11:00 AM - Mike T. (Dosing Session - Psilocybin 25mg)
- 3:00 PM - Jessica L. (Integration Session 1)

Pending Tasks:
- Complete documentation for yesterday's session (Tom R.)
- Review safety alert for Maria P. (new medication added)
- Approve session notes from supervisor
```

**During Session:**
1. Open patient's TreatmentPlan
2. System shows current ProtocolStep + documentation template
3. For dosing sessions:
   - Decision point evaluation (dose calculation)
   - Vitals logging interface (timestamped entries)
   - AI decision support panel (monitors for concerns)
4. Complete structured documentation
5. Mark step complete → System advances to next step

### Admin Workflow (Protocol Management)

**Creating New Protocol:**
1. Upload research paper (PDF)
2. AI extracts protocol structure
3. Review extracted data:
   - Edit steps, dosages, decision points
   - Add safety checks
   - Tag evidence sources
4. Configure contraindications
5. Set protocol metadata (therapy type, condition, evidence level)
6. Publish → Available to clinics

---

## 6. Frontend Architecture

### React Application Structure

```
src/
├── components/
│   ├── common/              # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   └── Badge.tsx
│   ├── protocols/
│   │   ├── ProtocolCard.tsx
│   │   ├── ProtocolBrowser.tsx
│   │   ├── ProtocolDetail.tsx
│   │   └── ProtocolStepViewer.tsx
│   ├── patient/
│   │   ├── ScreeningQuiz.tsx
│   │   ├── ProviderSearch.tsx
│   │   ├── TreatmentTimeline.tsx
│   │   └── SessionPreparation.tsx
│   ├── therapist/
│   │   ├── Dashboard.tsx
│   │   ├── PatientList.tsx
│   │   ├── SessionDocumentation.tsx
│   │   ├── VitalsLogger.tsx
│   │   └── DecisionPointEvaluator.tsx
│   ├── admin/
│   │   ├── ProtocolBuilder.tsx
│   │   ├── AIProtocolExtractor.tsx
│   │   └── SafetyCheckEditor.tsx
│   └── safety/
│       ├── ContraindicationChecker.tsx
│       ├── RiskScoreDisplay.tsx
│       └── AuditLogViewer.tsx
├── pages/
│   ├── patient/
│   │   ├── DiscoverProtocols.tsx
│   │   ├── MyTreatment.tsx
│   │   └── FindProvider.tsx
│   ├── therapist/
│   │   ├── TherapistDashboard.tsx
│   │   ├── PatientDetail.tsx
│   │   └── ActiveSession.tsx
│   └── admin/
│       ├── ProtocolManagement.tsx
│       └── SystemSettings.tsx
├── hooks/
│   ├── useProtocol.ts
│   ├── useTreatmentPlan.ts
│   ├── useAIAssist.ts
│   └── useSafetyCheck.ts
├── services/
│   ├── api.ts
│   ├── protocolService.ts
│   ├── patientService.ts
│   ├── therapistService.ts
│   └── aiService.ts
├── store/
│   ├── authSlice.ts
│   ├── protocolSlice.ts
│   └── sessionSlice.ts
└── types/
    ├── protocol.ts
    ├── patient.ts
    └── session.ts
```

### Design System (Tailwind)

**Colors:**
- Primary: Teal/Blue (trust, calm)
- Success: Green (safety checks passed)
- Warning: Amber (relative contraindications)
- Danger: Red (absolute contraindications)
- Accent: Purple (AI features)

**Typography:**
- Headings: Inter (clean, professional)
- Body: Inter (readable)
- Monospace: JetBrains Mono (clinical data, logs)

**Components:** Shadcn UI component library for consistency

---

## 7. Backend API Design

### FastAPI Application Structure

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   │
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── protocol.py
│   │   ├── user.py
│   │   ├── treatment.py
│   │   ├── session.py
│   │   └── safety.py
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── protocol.py
│   │   ├── user.py
│   │   ├── treatment.py
│   │   └── ai.py
│   │
│   ├── api/v1/
│   │   ├── auth.py
│   │   ├── protocols.py
│   │   ├── patients.py
│   │   ├── therapists.py
│   │   ├── admin.py
│   │   ├── safety.py
│   │   └── ai.py
│   │
│   ├── services/
│   │   ├── protocol_engine.py
│   │   ├── safety_service.py
│   │   ├── ai_service.py
│   │   ├── matching_service.py
│   │   └── audit_service.py
│   │
│   ├── core/
│   │   ├── security.py
│   │   ├── permissions.py
│   │   └── exceptions.py
│   │
│   └── utils/
│       ├── ai_prompts.py
│       ├── clinical_calculators.py
│       └── validators.py
│
├── alembic/
├── tests/
├── requirements.txt
└── Dockerfile
```

### Key API Endpoints

**Authentication & Users**
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/users/me`

**Protocols (Public/Patient)**
- `GET /api/v1/protocols` - Browse protocol library
- `GET /api/v1/protocols/{id}` - Protocol details
- `GET /api/v1/protocols/{id}/explanation` - AI-generated patient guide
- `POST /api/v1/protocols/{id}/pre-screen` - Pre-screening quiz

**Protocols (Admin)**
- `POST /api/v1/admin/protocols` - Create protocol
- `POST /api/v1/admin/protocols/extract` - AI extraction from PDF
- `PUT /api/v1/admin/protocols/{id}` - Update protocol
- `POST /api/v1/admin/protocols/{id}/publish` - Publish protocol

**Patient Journey**
- `GET /api/v1/patients/providers/search` - Find therapists/clinics
- `POST /api/v1/patients/consultation-request` - Request consultation
- `GET /api/v1/patients/treatment-plans` - My treatment plans
- `POST /api/v1/patients/consent/{plan_id}` - Sign informed consent

**Therapist Workflows**
- `GET /api/v1/therapist/dashboard` - Today's schedule
- `GET /api/v1/therapist/patients` - My patients
- `POST /api/v1/therapist/treatment-plans` - Create treatment plan
- `POST /api/v1/therapist/sessions/{id}/vitals` - Log vitals
- `POST /api/v1/therapist/sessions/{id}/documentation` - Save session notes
- `POST /api/v1/therapist/decision-points/{id}/evaluate` - Evaluate decision point

**Safety & Compliance**
- `POST /api/v1/safety/contraindication-check` - Run safety check
- `GET /api/v1/safety/risk-score/{patient_id}` - Calculate risk score
- `GET /api/v1/audit-logs` - View audit trail

**AI Services**
- `POST /api/v1/ai/extract-protocol` - Extract from research paper
- `POST /api/v1/ai/generate-patient-education` - Create patient guide
- `POST /api/v1/ai/decision-support` - Real-time clinical support

---

## 8. Security, Compliance & Deployment

### Security Architecture

**Authentication & Authorization**
- JWT access tokens (15min expiry)
- Refresh tokens (7 day expiry, httpOnly cookies)
- Argon2 password hashing
- Role-based access control (RBAC)
- Resource-level permissions

**Data Security**
- TLS 1.3 for all connections
- PostgreSQL encryption at rest
- Field-level encryption for sensitive PHI
- Audit all PHI access

**HIPAA Compliance**
- ✅ Access controls (unique user IDs, automatic logoff)
- ✅ Audit controls (comprehensive logging)
- ✅ Integrity controls (checksums, version tracking)
- ✅ Transmission security (TLS)
- ✅ Business associate agreements (Anthropic, Stripe)

### Simplified Deployment (GCP VM)

**Single VM Architecture:**

```
┌─────────────────────────────────────────────┐
│         GCP VM (e2-standard-4)              │
│  Ubuntu 22.04 LTS | 4 vCPU | 16GB RAM      │
├─────────────────────────────────────────────┤
│  ┌────────────────────────────────────┐    │
│  │   Nginx (Reverse Proxy + TLS)      │    │
│  │   Port 80/443                      │    │
│  └──────────┬──────────────┬──────────┘    │
│             │              │                │
│  ┌──────────▼─────┐  ┌────▼─────────────┐  │
│  │  Frontend      │  │  Backend         │  │
│  │  (Static)      │  │  (FastAPI)       │  │
│  └────────────────┘  └──────────────────┘  │
│                                             │
│  ┌──────────────────┐  ┌────────────────┐  │
│  │  PostgreSQL 15   │  │  Redis 7       │  │
│  └──────────────────┘  └────────────────┘  │
│                                             │
│  Docker Compose orchestration               │
└─────────────────────────────────────────────┘
```

**Deployment Process:**
1. Create GCP VM (e2-standard-4, Ubuntu 22.04)
2. Configure firewall rules (ports 80, 443)
3. Run `deploy.sh` script which handles:
   - System updates
   - Docker + Docker Compose installation
   - SSL certificate generation (Let's Encrypt)
   - Nginx configuration
   - Application build and deployment
   - Database migrations

**Key Files:**
- `docker-compose.prod.yml` - Production orchestration
- `deploy.sh` - Automated deployment script
- `backup.sh` - Automated database backups
- `nginx/nginx.conf` - Nginx reverse proxy config

---

## 9. Example Protocols

### Protocol 1: Psilocybin for Treatment-Resistant Depression

**Based on:** COMP360 Phase 3 trials (Goodwin et al., N Engl J Med 2022)

**Overview:**
- Duration: 12 weeks
- Total sessions: 8
- Evidence level: Phase 3 trial data

**Steps:**
1. Initial Psychiatric Evaluation (90 min)
2. Medical Clearance (60 min)
3. Preparation Session 1 - Building Trust (90 min)
4. Preparation Session 2 - Set & Setting (90 min)
5. **DECISION POINT:** Dose Determination (25mg standard)
6. Psilocybin Dosing Session (8 hours)
   - Vitals every 30 minutes
   - Medical supervisor on-site
   - MEQ30 mystical experience scale
7. Integration Session 1 - Day After (60 min)
8. Integration Session 2 - Week 1 (60 min)
9. **DECISION POINT:** Evaluate Response (PHQ-9 improvement)
10. Maintenance Integration (4 weekly sessions)

**Safety Checks:**
- Absolute contraindications: Active psychosis, schizophrenia spectrum
- Relative contraindications: Family history of psychosis, cardiovascular disease
- Medication interactions: SSRIs, SNRIs (tapering may be required)

### Protocol 2: MDMA-Assisted Therapy for PTSD

**Based on:** MAPS Phase 3 trials (Mitchell et al., Nature Medicine 2021)

**Overview:**
- Duration: 18 weeks
- Total sessions: 15
- Evidence level: FDA approved

**Steps:**
1. CAPS-5 PTSD diagnosis confirmation
2. Preparatory sessions (3 x 90 min)
3. MDMA Session 1 (80-120mg initial dose + supplemental)
4. Integration sessions (3 x 90 min)
5. MDMA Session 2
6. Integration sessions (3 x 90 min)
7. MDMA Session 3
8. Final integration sessions

### Protocol 3: Ketamine Infusion for Depression

**Overview:**
- Duration: 6 weeks
- Sessions: 6 infusions (twice weekly)
- Dose: 0.5mg/kg IV over 40 minutes
- Evidence level: Standard of care

**Monitoring:**
- Vitals every 10 minutes
- Dissociation scale tracking
- Blood pressure monitoring (critical)

---

## 10. Go-to-Market Strategy

### Target Customer Segments

**1. Existing Psychedelic Clinics (Primary)**
- Profile: Newly licensed ketamine/psilocybin clinics
- Market size: 100-500 clinics in US by 2026
- Pain points: Paper protocols, compliance burden
- Value prop: "Launch with validated protocols in days"
- Pricing: $500-1000/month per clinic

**2. Mental Health Group Practices**
- Profile: Psychiatry practices adding psychedelic services
- Pain points: Don't know where to start
- Value prop: "Turnkey protocol system + compliance"
- Pricing: $1000-2000/month

**3. Research Institutions**
- Profile: Universities running psychedelic trials
- Pain points: Expensive custom trial software
- Value prop: "Protocol engine for adaptive trials"
- Pricing: Enterprise ($10k-50k/year)

### Launch Plan (Months 1-6)

**Month 1-2:** Build MVP
- Core protocol engine
- Patient + therapist portals
- 3 example protocols
- Deploy to GCP VM

**Month 3:** Beta Testing
- Recruit 3-5 beta clinics
- Free during beta
- Iterate based on feedback

**Month 4:** Regulatory Review
- HIPAA compliance audit
- Security testing
- Compliance documentation

**Month 5:** Launch Prep
- Finalize pricing
- Sales materials
- Demo environment

**Month 6:** Public Launch
- Conference announcement
- Outbound sales to 100 clinics
- Target: 10 paying customers

### Revenue Model

**Tier 1 - Solo Practitioner:** $299/month
- 1 therapist, up to 20 patients
- All protocols, email support

**Tier 2 - Small Clinic:** $799/month
- Up to 5 therapists, 100 patients
- Custom protocol builder, priority support

**Tier 3 - Group Practice:** $1,999/month
- Unlimited therapists/patients
- White-label option, custom integrations

**Enterprise:** Custom pricing
- Research institutions, API access

### Key Metrics

**Acquisition:**
- Clinics in pipeline
- Demo → Paying conversion rate
- Customer acquisition cost (CAC)

**Activation:**
- Time to first patient treated
- Therapist onboarding completion

**Retention:**
- Monthly recurring revenue (MRR)
- Churn rate
- Net revenue retention

**Clinical Outcomes:**
- Protocol completion rates
- Adverse event frequency
- Patient outcome improvements (PHQ-9, CAPS-5)

---

## Appendix: Feature Prioritization

### MVP (Must-Have for 2-3 Month Launch)

✅ Pre-loaded psychedelic protocols (psilocybin, MDMA, ketamine)
✅ Patient discovery & matching with therapists/clinics
✅ Patient screening & tiered contraindication checks
✅ Session booking & scheduling
✅ Tiered session documentation (prep/dosing/integration)
✅ Manual vitals logging during sessions
✅ Dynamic protocol branching (decision points)
✅ AI protocol creation from research papers
✅ Clinic + solo practitioner support (hybrid model)
✅ Audit trails & compliance logging

### Phase 2 (Post-Launch)

- AI patient education materials
- AI clinical decision support
- Payment processing (Stripe integration)
- Automated wearable device integration
- EMR/EHR integrations
- Advanced analytics dashboard
- Outcomes research tools

---

**End of Design Document**
