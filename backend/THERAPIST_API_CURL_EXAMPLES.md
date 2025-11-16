# Therapist API Endpoints - cURL Examples

This document provides sample cURL commands for all therapist endpoints implemented in Task 12.

## Prerequisites

1. Start the server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Register a therapist user and obtain an access token:
   ```bash
   # Register therapist
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "therapist@clinic.com",
       "password": "SecurePass123!",
       "role": "therapist"
     }'

   # Login to get access token
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "therapist@clinic.com",
       "password": "SecurePass123!"
     }'
   ```

3. Save the `access_token` from the login response and use it in the following commands:
   ```bash
   export TOKEN="your_access_token_here"
   ```

---

## 1. Get Therapist Dashboard

Get today's sessions, pending tasks, and summary statistics.

```bash
curl -X GET "http://localhost:8000/api/v1/therapist/dashboard" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "today_sessions": [
    {
      "id": 1,
      "patient_id": 2,
      "patient_email": "patient@example.com",
      "scheduled_at": "2025-11-16T14:00:00",
      "status": "scheduled",
      "location": "in_person",
      "step_title": "Initial Screening"
    }
  ],
  "pending_tasks": [
    {
      "task_type": "documentation",
      "session_id": 3,
      "treatment_plan_id": null,
      "description": "Complete documentation for session 3",
      "priority": "high",
      "due_date": null
    }
  ],
  "active_patients_count": 5,
  "upcoming_sessions_count": 8
}
```

---

## 2. Get Patient List

Get all patients assigned to this therapist with treatment information.

```bash
curl -X GET "http://localhost:8000/api/v1/therapist/patients" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
[
  {
    "id": 2,
    "email": "patient1@example.com",
    "date_of_birth": "1990-05-15",
    "treatment_plan_id": 1,
    "protocol_name": "Psilocybin for Depression",
    "treatment_status": "active",
    "next_session": "2025-11-20T10:00:00"
  },
  {
    "id": 3,
    "email": "patient2@example.com",
    "date_of_birth": "1985-08-22",
    "treatment_plan_id": 2,
    "protocol_name": "MDMA for PTSD",
    "treatment_status": "screening",
    "next_session": "2025-11-18T14:30:00"
  }
]
```

---

## 3. Create Treatment Plan

Create a new treatment plan for a patient.

```bash
curl -X POST "http://localhost:8000/api/v1/therapist/treatment-plans" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 2,
    "protocol_id": 1,
    "start_date": "2025-11-16T09:00:00",
    "customizations": {
      "notes": "Patient has severe depression, starting with lower dose",
      "modifications": ["extended_integration_sessions"]
    }
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "patient_id": 2,
  "therapist_id": 1,
  "clinic_id": 1,
  "protocol_id": 1,
  "protocol_version": "1.0",
  "status": "active",
  "start_date": "2025-11-16T09:00:00",
  "estimated_completion": null,
  "customizations": {
    "notes": "Patient has severe depression, starting with lower dose",
    "modifications": ["extended_integration_sessions"]
  },
  "created_at": "2025-11-16T12:00:00"
}
```

---

## 4. Get Session Details

Get detailed information about a specific session.

```bash
curl -X GET "http://localhost:8000/api/v1/therapist/sessions/1" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "treatment_plan_id": 1,
  "protocol_step_id": 1,
  "scheduled_at": "2025-11-16T14:00:00",
  "actual_start": "2025-11-16T14:05:00",
  "actual_end": null,
  "status": "in_progress",
  "location": "in_person",
  "therapist_id": 1,
  "patient_id": 2,
  "patient_email": "patient@example.com",
  "step_title": "Initial Screening",
  "step_description": "Comprehensive psychiatric evaluation",
  "vitals": [
    {
      "blood_pressure": "120/80",
      "heart_rate": 72,
      "temperature": 98.6,
      "spo2": 98,
      "timestamp": "2025-11-16T14:10:00",
      "notes": "Baseline vitals normal"
    }
  ],
  "documentation": {
    "therapist_notes": "Patient appears calm and engaged",
    "patient_subjective_notes": "Feeling hopeful about treatment",
    "clinical_scales": {
      "PHQ-9": 18,
      "GAD-7": 12
    },
    "adverse_events": []
  }
}
```

---

## 5. Log Session Vitals

Log vitals during a treatment session.

```bash
curl -X POST "http://localhost:8000/api/v1/therapist/sessions/1/vitals" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "blood_pressure": "118/76",
    "heart_rate": 68,
    "temperature": 98.4,
    "spo2": 99,
    "timestamp": "2025-11-16T14:30:00",
    "notes": "30 minutes post-dose, patient stable"
  }'
```

**Expected Response:**
```json
{
  "message": "Vitals logged successfully",
  "vitals_logged": 2,
  "session_id": 1
}
```

---

## 6. Save Session Documentation

Save or update session documentation including notes, clinical scales, and adverse events.

```bash
curl -X POST "http://localhost:8000/api/v1/therapist/sessions/1/documentation" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "therapist_notes": "Patient responded well to initial dose. No adverse effects observed. Discussed integration themes.",
    "patient_subjective_notes": "Patient reported feeling calm and introspective. Noted visual enhancements and emotional openness.",
    "clinical_scales": {
      "PHQ-9": 15,
      "GAD-7": 10,
      "MEQ30": 25,
      "Mystical_Experience": "moderate"
    },
    "adverse_events": []
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "treatment_session_id": 1,
  "message": "Documentation saved successfully"
}
```

---

## 7. Save Session with Adverse Events

Example of documenting a session with adverse events.

```bash
curl -X POST "http://localhost:8000/api/v1/therapist/sessions/1/documentation" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "therapist_notes": "Patient experienced mild nausea at T+45min. Resolved with ginger tea.",
    "adverse_events": [
      {
        "event_type": "gastrointestinal",
        "severity": "mild",
        "description": "Patient reported mild nausea",
        "timestamp": "2025-11-16T14:45:00",
        "action_taken": "Administered ginger tea. Nausea resolved within 15 minutes."
      }
    ]
  }'
```

---

## 8. Complete Session

Mark a session as completed.

```bash
curl -X POST "http://localhost:8000/api/v1/therapist/sessions/1/complete" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "status": "completed",
  "actual_end": "2025-11-16T18:00:00",
  "message": "Session completed successfully"
}
```

---

## 9. Evaluate Decision Point

Evaluate a decision point in the treatment protocol.

```bash
curl -X POST "http://localhost:8000/api/v1/therapist/decision-points/5/evaluate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "treatment_plan_id": 1,
    "evaluation_criteria": {
      "phq9_baseline": 20,
      "phq9_current": 12,
      "phq9_reduction": 8,
      "response_category": "strong_response",
      "adverse_events_count": 0,
      "patient_satisfaction": "high"
    },
    "recommendation": "continue",
    "notes": "Patient showing strong response to treatment. PHQ-9 reduced by 40%. Recommend continuing with next dosing session as planned."
  }'
```

**Expected Response:**
```json
{
  "decision_point_id": 5,
  "treatment_plan_id": 1,
  "recommendation": "continue",
  "evaluation_data": {
    "phq9_baseline": 20,
    "phq9_current": 12,
    "phq9_reduction": 8,
    "response_category": "strong_response",
    "adverse_events_count": 0,
    "patient_satisfaction": "high"
  },
  "message": "Decision point evaluated successfully",
  "timestamp": "2025-11-16T12:00:00"
}
```

---

## Error Responses

### Unauthorized Access (No Token)
```bash
curl -X GET "http://localhost:8000/api/v1/therapist/dashboard"
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authenticated"
}
```

### Insufficient Permissions (Patient trying to access therapist endpoint)
```bash
# Login as patient
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "password123"
  }'

# Try to access therapist dashboard
curl -X GET "http://localhost:8000/api/v1/therapist/dashboard" \
  -H "Authorization: Bearer $PATIENT_TOKEN"
```

**Response (403 Forbidden):**
```json
{
  "detail": "Insufficient permissions. Required roles: therapist"
}
```

### Session Not Found
```bash
curl -X GET "http://localhost:8000/api/v1/therapist/sessions/99999" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (404 Not Found):**
```json
{
  "detail": "Session not found"
}
```

### Accessing Another Therapist's Session
```bash
curl -X GET "http://localhost:8000/api/v1/therapist/sessions/5" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to access this session"
}
```

---

## Complete Workflow Example

Here's a complete workflow from therapist registration to completing a session:

```bash
# 1. Register therapist
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@clinic.com",
    "password": "SecurePass123!",
    "role": "therapist"
  }'

# 2. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@clinic.com",
    "password": "SecurePass123!"
  }' | jq -r '.access_token')

# 3. Check dashboard
curl -X GET "http://localhost:8000/api/v1/therapist/dashboard" \
  -H "Authorization: Bearer $TOKEN"

# 4. View patients
curl -X GET "http://localhost:8000/api/v1/therapist/patients" \
  -H "Authorization: Bearer $TOKEN"

# 5. Create treatment plan for a patient
curl -X POST "http://localhost:8000/api/v1/therapist/treatment-plans" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 2,
    "protocol_id": 1,
    "start_date": "2025-11-16T09:00:00"
  }'

# 6. View session details
curl -X GET "http://localhost:8000/api/v1/therapist/sessions/1" \
  -H "Authorization: Bearer $TOKEN"

# 7. Log vitals during session
curl -X POST "http://localhost:8000/api/v1/therapist/sessions/1/vitals" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "blood_pressure": "120/80",
    "heart_rate": 72,
    "temperature": 98.6,
    "spo2": 98,
    "timestamp": "2025-11-16T14:30:00"
  }'

# 8. Save session documentation
curl -X POST "http://localhost:8000/api/v1/therapist/sessions/1/documentation" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "therapist_notes": "Session went well. Patient responsive.",
    "clinical_scales": {
      "PHQ-9": 15
    }
  }'

# 9. Complete session
curl -X POST "http://localhost:8000/api/v1/therapist/sessions/1/complete" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Notes

- All timestamps should be in ISO 8601 format
- The `Authorization` header must include the Bearer token obtained from login
- Therapists can only access their own patients' data
- Session documentation supports incremental updates
- Vitals can be logged multiple times during a session
- Clinical scales should use standardized scale names (PHQ-9, GAD-7, MEQ30, etc.)

## API Documentation

For interactive API documentation, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
