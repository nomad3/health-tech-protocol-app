# Treatment Protocol Workflow System

## Overview

The PsyProtocol platform includes a sophisticated protocol workflow engine that manages complex treatment protocols with decision points, safety checks, and dynamic branching logic. This system allows protocols to be defined in JSON format and executed by the `ProtocolEngine`.

## Architecture

### Components

1. **Protocol JSON Files** (`backend/examples/*.json`)
   - Define complete treatment protocols with all steps, rules, and safety checks
   - Include decision points, contraindications, and evaluation criteria
   - Support multiple therapy types (psilocybin, MDMA, ketamine, TRT, chemotherapy, etc.)

2. **Protocol Engine** (`backend/app/services/protocol_engine.py`)
   - Evaluates decision points using patient data
   - Determines next steps based on protocol rules
   - Handles branching logic and conditional workflows
   - Validates protocol completion

3. **Safety Service** (`backend/app/services/safety_service.py`)
   - Evaluates contraindications and safety checks
   - Blocks progression when absolute contraindications are present
   - Provides warnings for relative contraindications
   - Tracks risk factors for monitoring

4. **Database Models** (`backend/app/models/`)
   - `Protocol`: Main protocol definition
   - `ProtocolStep`: Individual steps with rules and requirements
   - `SafetyCheck`: Contraindications and safety validations
   - `TreatmentPlan`: Patient-specific protocol instance
   - `TreatmentSession`: Individual session execution records

## Protocol JSON Structure

### Example: Psilocybin Protocol

```json
{
  "protocol": {
    "name": "Psilocybin-Assisted Therapy for Treatment-Resistant Depression",
    "version": "1.0",
    "therapy_type": "psilocybin_psychedelic",
    "condition_treated": "Treatment-Resistant Depression (TRD)",
    "evidence_level": "phase_3_clinical_trial",
    "overview": "Evidence-based protocol...",
    "duration_weeks": 12,
    "total_sessions": 15,
    "evidence_sources": [...]
  },
  "steps": [
    {
      "sequence_order": 1,
      "step_type": "screening",
      "title": "Comprehensive Psychiatric Evaluation",
      "description": "Detailed assessment...",
      "duration_minutes": 90,
      "required_roles": ["psychiatrist", "clinical_psychologist"],
      "clinical_scales": ["MADRS", "PHQ-9", "GAD-7"],
      "documentation_requirements": {...}
    },
    {
      "sequence_order": 3,
      "step_type": "decision_point",
      "title": "Safety & Eligibility Determination",
      "evaluation_rules": {
        "type": "safety_assessment",
        "absolute_contraindications": [
          {
            "condition": "psychotic_disorder_history",
            "description": "Personal history of schizophrenia...",
            "action": "exclude_from_treatment"
          }
        ],
        "medication_contraindications": [...]
      },
      "branch_outcomes": [
        {
          "outcome_id": "eligible_for_treatment",
          "next_step": 4
        },
        {
          "outcome_id": "excluded_safety",
          "next_step": "exit_protocol"
        }
      ]
    }
  ]
}
```

## Decision Point Types

### 1. Single Factor Evaluation

Evaluates one patient characteristic to determine the next step.

```json
{
  "step_type": "decision_point",
  "evaluation_rules": {
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
  "branch_outcomes": [
    {"outcome_id": "mild", "next_step_order": 3},
    {"outcome_id": "moderate", "next_step_order": 4},
    {"outcome_id": "severe", "next_step_order": 5}
  ]
}
```

### 2. Multi-Factor Evaluation

Combines multiple patient characteristics using a decision matrix.

```json
{
  "evaluation_rules": {
    "type": "multi_factor",
    "factors": [
      {
        "factor": "depression_severity",
        "operator": "in_range",
        "ranges": [
          {"min": 0, "max": 20, "value": "mild"},
          {"min": 20, "max": 100, "value": "severe"}
        ]
      },
      {
        "factor": "anxiety_level",
        "operator": "threshold",
        "thresholds": [
          {"min": 0, "max": 10, "value": "low"},
          {"min": 10, "max": 100, "value": "high"}
        ]
      }
    ],
    "decision_matrix": {
      "mild + low": "standard_protocol",
      "mild + high": "anxiety_adapted_protocol",
      "severe + low": "intensive_protocol",
      "severe + high": "stabilization_first",
      "default": "standard_protocol"
    }
  }
}
```

## Supported Operators

### in_range
Checks if a numeric value falls within specified ranges.

```json
{
  "operator": "in_range",
  "ranges": [
    {"min": 0, "max": 30, "value": "low"},
    {"min": 30, "max": 70, "value": "medium"},
    {"min": 70, "max": 100, "value": "high"}
  ]
}
```

### threshold
Evaluates value against threshold boundaries.

```json
{
  "operator": "threshold",
  "thresholds": [
    {"min": 0, "max": 50, "value": "below_threshold"},
    {"min": 50, "max": 100, "value": "above_threshold"}
  ]
}
```

### equals
Checks for exact value matches.

```json
{
  "operator": "equals",
  "conditions": [
    {"value": "F33.2", "result": "major_depression"},
    {"value": "F43.1", "result": "ptsd"}
  ]
}
```

### boolean
Evaluates true/false conditions.

```json
{
  "operator": "boolean",
  "true_value": "proceed_with_treatment",
  "false_value": "defer_treatment"
}
```

## Safety Checks

### Absolute Contraindications
Block progression completely.

```json
{
  "check_type": "absolute_contraindication",
  "condition": {
    "type": "diagnosis",
    "value": "F20",
    "operator": "contains"
  },
  "severity": "blocking",
  "override_allowed": "false",
  "evidence_source": "Psilocybin can exacerbate psychotic symptoms"
}
```

### Relative Contraindications
Provide warnings but allow override.

```json
{
  "check_type": "relative_contraindication",
  "condition": {
    "type": "medication",
    "value": "SSRI",
    "operator": "class_match"
  },
  "severity": "warning",
  "override_allowed": "true",
  "evidence_source": "SSRIs may reduce psilocybin efficacy"
}
```

### Risk Factors
Informational only, don't block progression.

```json
{
  "check_type": "risk_factor",
  "condition": {
    "type": "vital_sign",
    "name": "systolic_bp",
    "operator": "greater_than",
    "threshold": 140
  },
  "severity": "info",
  "override_allowed": "true",
  "evidence_source": "Monitor BP closely during session"
}
```

## Protocol Execution Flow

### 1. Protocol Import
```bash
# Import all JSON protocols into database
python seed_database.py
```

### 2. Treatment Plan Creation
```python
from app.models import TreatmentPlan, TreatmentStatus

plan = TreatmentPlan(
    patient_id=patient.id,
    therapist_id=therapist.id,
    protocol_id=protocol.id,
    protocol_version="1.0",
    status=TreatmentStatus.SCREENING,
    start_date=datetime.utcnow()
)
```

### 3. Step Progression
```python
from app.services.protocol_engine import ProtocolEngine

engine = ProtocolEngine()

# Get current step
current_step = engine.get_current_step(plan)

# Check safety before progression
patient_data = {
    "age": 35,
    "diagnoses": ["F33.2"],
    "medications": [],
    "caps5_score": 45
}

progression_check = engine.can_progress_to_step(
    plan, current_step, patient_data, db
)

if progression_check['can_progress']:
    # Create session
    session = TreatmentSession(
        treatment_plan_id=plan.id,
        protocol_step_id=current_step.id,
        status=SessionStatus.COMPLETED
    )

    # Get next step (handles decision points automatically)
    next_step = engine.get_next_step(
        protocol, current_step, patient_data
    )
```

### 4. Decision Point Evaluation
```python
# For decision point steps
if current_step.step_type == StepType.DECISION_POINT:
    outcome = engine.evaluate_decision_point(
        current_step, patient_data
    )
    # Engine automatically branches to correct next step
```

### 5. Protocol Completion
```python
is_complete = engine.is_protocol_complete(plan)

if is_complete:
    plan.status = TreatmentStatus.COMPLETED
```

## Available Protocol Files

1. **psilocybin_depression_detailed_protocol.json**
   - 15 steps with detailed preparation, dosing, and integration
   - Decision points for dose determination
   - Comprehensive safety checks

2. **mdma_ptsd_maps_protocol.json**
   - MAPS Phase 3 protocol
   - Severity-based treatment planning
   - CAPS-5 assessment integration

3. **ketamine_depression_protocol.json**
   - Infusion-based protocol
   - Dose escalation logic
   - Response monitoring

4. **lsd_microdosing_protocol.json**
   - Microdosing schedule
   - Cognitive enhancement tracking
   - Safety monitoring

5. **testosterone_optimization_protocol.json**
   - Lab-based decision points
   - Dose adjustment algorithms
   - Long-term monitoring

6. **testosterone_replacement_protocol.json**
   - Standard TRT protocol
   - Follow-up scheduling
   - Symptom tracking

7. **chemotherapy_protocol.json**
   - Cycle-based treatment
   - Toxicity monitoring
   - Dose modification rules

8. **stem_cell_therapy_protocol.json**
   - Multi-phase protocol
   - Eligibility screening
   - Post-treatment monitoring

## Testing

### Run Protocol Execution Demos
```bash
cd backend
python demo_protocol_execution.py
```

This demonstrates:
- Linear protocol execution
- Decision point branching
- Safety check validation
- Multi-therapy type support

### Run Unit Tests
```bash
pytest tests/test_services/test_protocol_execution.py -v
```

## API Integration

### Get Current Step
```http
GET /api/v1/therapist/treatment-plans/{plan_id}/current-step
```

### Evaluate Decision Point
```http
POST /api/v1/therapist/treatment-plans/{plan_id}/evaluate-decision
Content-Type: application/json

{
  "patient_data": {
    "caps5_score": 45,
    "depression_severity": 28
  }
}
```

### Check Safety
```http
POST /api/v1/therapist/treatment-plans/{plan_id}/check-safety
Content-Type: application/json

{
  "patient_data": {
    "diagnoses": ["F33.2"],
    "medications": [{"name": "Sertraline", "class": "SSRI"}],
    "vital_signs": {"systolic_bp": 135}
  }
}
```

## Adding New Protocols

### 1. Create JSON File
Create a new file in `backend/examples/` following the structure above.

### 2. Add to Import List
Edit `backend/seed_database.py`:

```python
PROTOCOL_FILES = [
    # ... existing files ...
    "your_new_protocol.json",
]
```

### 3. Run Import
```bash
python seed_database.py
```

### 4. Verify
```bash
# Check protocol was imported
psql -d psyprotocol -c "SELECT id, name, version FROM protocols;"
```

## Best Practices

1. **Decision Points**: Always provide a "default" outcome in decision matrices
2. **Safety Checks**: Use absolute contraindications sparingly - only for genuine safety risks
3. **Step Sequencing**: Use gaps in sequence_order (1, 5, 10, 15) to allow future insertions
4. **Evidence Sources**: Always cite clinical trial data or published guidelines
5. **Testing**: Test all decision point branches with representative patient data

## Future Enhancements

- [ ] Visual protocol builder UI
- [ ] Real-time protocol execution monitoring
- [ ] AI-assisted decision point evaluation
- [ ] Protocol versioning and migration
- [ ] Outcome tracking and protocol optimization
- [ ] Multi-site protocol synchronization

## Resources

- Protocol Engine: `backend/app/services/protocol_engine.py`
- Safety Service: `backend/app/services/safety_service.py`
- Demo Script: `backend/demo_protocol_execution.py`
- Unit Tests: `backend/tests/test_services/test_protocol_execution.py`
- Example Protocols: `backend/examples/*.json`
