# Admin Protocol Management API - Sample Workflow

This document demonstrates the complete admin protocol creation workflow using curl commands.

## Prerequisites

1. Server running: `uvicorn app.main:app --reload`
2. Admin user created and logged in

## Step 1: Register Admin User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@psyprotocol.com",
    "password": "SecureAdminPass123!",
    "role": "platform_admin"
  }'
```

Response:
```json
{
  "id": 1,
  "email": "admin@psyprotocol.com",
  "role": "platform_admin",
  "is_active": true,
  "created_at": "2025-11-15T12:00:00"
}
```

## Step 2: Login to Get Access Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@psyprotocol.com",
    "password": "SecureAdminPass123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the access_token for subsequent requests!**

## Step 3: Create a New Protocol

```bash
curl -X POST http://localhost:8000/api/v1/admin/protocols \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Psilocybin for Treatment-Resistant Depression",
    "version": "1.0",
    "therapy_type": "psilocybin",
    "condition_treated": "treatment_resistant_depression",
    "evidence_level": "phase_3_trial",
    "overview": "Evidence-based protocol for TRD based on Johns Hopkins and Imperial College research",
    "duration_weeks": 12,
    "total_sessions": 6,
    "evidence_sources": [
      "https://pubmed.ncbi.nlm.nih.gov/33852451/",
      "https://pubmed.ncbi.nlm.nih.gov/34265266/"
    ]
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Psilocybin for Treatment-Resistant Depression",
  "version": "1.0",
  "status": "draft",
  "therapy_type": "psilocybin",
  "condition_treated": "treatment_resistant_depression",
  "evidence_level": "phase_3_trial",
  "overview": "Evidence-based protocol for TRD...",
  "duration_weeks": 12,
  "total_sessions": 6,
  "created_at": "2025-11-15T12:05:00",
  "updated_at": "2025-11-15T12:05:00"
}
```

**Save the protocol ID (e.g., 1) for subsequent requests!**

## Step 4: Add Protocol Steps

### Step 4.1: Add Screening Step

```bash
curl -X POST http://localhost:8000/api/v1/admin/protocols/1/steps \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "sequence_order": 1,
    "step_type": "screening",
    "title": "Initial Psychiatric Evaluation",
    "description": "Comprehensive psychiatric assessment including diagnostic interview, mental status exam, and screening for contraindications",
    "duration_minutes": 90,
    "required_roles": ["therapist", "medical_director"],
    "clinical_scales": ["PHQ-9", "GAD-7", "CADSS", "MEQ30"]
  }'
```

Response:
```json
{
  "id": 1,
  "protocol_id": 1,
  "sequence_order": 1,
  "step_type": "screening",
  "title": "Initial Psychiatric Evaluation",
  "description": "Comprehensive psychiatric assessment...",
  "duration_minutes": 90,
  "required_roles": ["therapist", "medical_director"],
  "clinical_scales": ["PHQ-9", "GAD-7", "CADSS", "MEQ30"],
  "created_at": "2025-11-15T12:10:00"
}
```

### Step 4.2: Add Preparation Step

```bash
curl -X POST http://localhost:8000/api/v1/admin/protocols/1/steps \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "sequence_order": 2,
    "step_type": "preparation",
    "title": "Preparatory Session 1 - Trust Building",
    "description": "Build therapeutic alliance, discuss intentions, set expectations",
    "duration_minutes": 60,
    "required_roles": ["therapist"]
  }'
```

### Step 4.3: Add Dosing Session Step

```bash
curl -X POST http://localhost:8000/api/v1/admin/protocols/1/steps \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "sequence_order": 3,
    "step_type": "dosing",
    "title": "Psilocybin Dosing Session (25mg)",
    "description": "6-8 hour dosing session with continuous monitoring",
    "duration_minutes": 480,
    "required_roles": ["therapist", "medical_monitor"],
    "vitals_monitoring": {
      "blood_pressure": {"frequency_minutes": 30, "required": true},
      "heart_rate": {"frequency_minutes": 30, "required": true},
      "temperature": {"frequency_minutes": 60, "required": true}
    }
  }'
```

### Step 4.4: Add Integration Step

```bash
curl -X POST http://localhost:8000/api/v1/admin/protocols/1/steps \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "sequence_order": 4,
    "step_type": "integration",
    "title": "Integration Session 1 - Day After",
    "description": "Process experience, identify insights, connect to therapeutic goals",
    "duration_minutes": 90,
    "required_roles": ["therapist"]
  }'
```

## Step 5: Add Safety Checks to Screening Step

### Safety Check 1: Absolute Contraindication - Psychosis

```bash
curl -X POST http://localhost:8000/api/v1/admin/protocols/1/steps/1/safety-checks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "check_type": "absolute_contraindication",
    "condition": {
      "field": "psychosis_history",
      "operator": "equals",
      "value": true
    },
    "severity": "blocking",
    "override_allowed": "false",
    "evidence_source": "Carhart-Harris et al. 2018, Safety guidelines"
  }'
```

Response:
```json
{
  "id": 1,
  "protocol_step_id": 1,
  "check_type": "absolute_contraindication",
  "condition": {
    "field": "psychosis_history",
    "operator": "equals",
    "value": true
  },
  "severity": "blocking",
  "override_allowed": "false",
  "evidence_source": "Carhart-Harris et al. 2018, Safety guidelines",
  "created_at": "2025-11-15T12:15:00"
}
```

### Safety Check 2: Relative Contraindication - Cardiovascular Disease

```bash
curl -X POST http://localhost:8000/api/v1/admin/protocols/1/steps/1/safety-checks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "check_type": "relative_contraindication",
    "condition": {
      "field": "cardiovascular_disease",
      "operator": "equals",
      "value": true
    },
    "severity": "warning",
    "override_allowed": "true",
    "override_requirements": {
      "required_approval": "medical_director",
      "additional_screening": ["ECG", "Cardiology_Consult"]
    },
    "evidence_source": "FDA Phase 2 safety protocols"
  }'
```

## Step 6: Update a Protocol Step

```bash
curl -X PUT http://localhost:8000/api/v1/admin/protocols/1/steps/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Initial Comprehensive Psychiatric Assessment",
    "duration_minutes": 120
  }'
```

## Step 7: Update Protocol Metadata

```bash
curl -X PUT http://localhost:8000/api/v1/admin/protocols/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "overview": "Updated: Evidence-based protocol for TRD based on Johns Hopkins, Imperial College, and USONA Institute research. Phase 3 trial data shows 67% remission rate.",
    "total_sessions": 8
  }'
```

## Step 8: Publish Protocol

```bash
curl -X POST http://localhost:8000/api/v1/admin/protocols/1/publish \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{}'
```

Response:
```json
{
  "id": 1,
  "name": "Psilocybin for Treatment-Resistant Depression",
  "version": "1.0",
  "status": "active",
  "therapy_type": "psilocybin",
  "condition_treated": "treatment_resistant_depression",
  "evidence_level": "phase_3_trial",
  "overview": "Updated: Evidence-based protocol...",
  "duration_weeks": 12,
  "total_sessions": 8,
  "created_at": "2025-11-15T12:05:00",
  "updated_at": "2025-11-15T12:20:00"
}
```

## Step 9: Delete a Step (if needed)

```bash
curl -X DELETE http://localhost:8000/api/v1/admin/protocols/1/steps/4 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "message": "Step deleted successfully"
}
```

## Step 10: Archive a Protocol

```bash
curl -X DELETE http://localhost:8000/api/v1/admin/protocols/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "message": "Protocol archived successfully"
}
```

---

## Test Non-Admin Access (Should Fail with 403)

```bash
# First, register as a patient
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "PatientPass123!",
    "role": "patient"
  }'

# Login as patient
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "PatientPass123!"
  }'

# Try to create protocol with patient token (should fail)
curl -X POST http://localhost:8000/api/v1/admin/protocols \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer PATIENT_ACCESS_TOKEN" \
  -d '{
    "name": "Test Protocol",
    "version": "1.0",
    "therapy_type": "psilocybin",
    "condition_treated": "depression",
    "evidence_level": "phase_3_trial"
  }'
```

Expected Response:
```json
{
  "detail": "Insufficient permissions. Required roles: platform_admin"
}
```

---

## Complete Workflow Summary

1. **Register admin user** → Get admin credentials
2. **Login** → Get access token
3. **Create protocol** (status: draft) → Get protocol ID
4. **Add steps** to protocol → Build protocol workflow
5. **Add safety checks** to steps → Define contraindications
6. **Update protocol/steps** as needed → Refine protocol
7. **Publish protocol** (status: active) → Make available for use
8. **Archive protocol** when deprecated → Soft delete

All admin endpoints require `PLATFORM_ADMIN` role and are protected by JWT authentication.
