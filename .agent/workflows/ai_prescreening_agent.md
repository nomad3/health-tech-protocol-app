---
description: Implementation plan for AI-driven Pre-screening Agent
---

# AI Pre-screening Agent Implementation Plan

This workflow outlines the steps to transform the static pre-screening form into an interactive chat with an intelligent agent.

## 1. Backend Implementation

### 1.1. New API Endpoints
- Create `POST /api/v1/patients/protocols/{protocol_id}/chat/start`: Initialize a new chat session.
- Create `POST /api/v1/patients/protocols/{protocol_id}/chat/message`: Send a user message and get the agent's response.
- Create `GET /api/v1/patients/protocols/{protocol_id}/chat/history`: Retrieve chat history (optional, for persistence).

### 1.2. Data Model
- Define a `ChatSession` model (or use Redis) to store:
    - `session_id`
    - `user_id`
    - `protocol_id`
    - `conversation_history` (List of messages)
    - `collected_data` (Extracted answers: age, medical history, etc.)
    - `status` (IN_PROGRESS, COMPLETED)

### 1.3. LLM Integration
- Use `langchain` or direct API calls to Anthropic/OpenAI.
- **System Prompt**: Design a prompt that instructs the AI to:
    - Act as a compassionate medical assistant.
    - Ask pre-screening questions one by one (Age, Medical History, Medications, etc.).
    - Validate answers.
    - Extract structured data from the conversation.
    - Determine eligibility based on criteria (e.g., Age >= 18, no psychosis).

### 1.4. Eligibility Logic
- The AI should eventually output a structured result (JSON) indicating eligibility, risk level, and recommendations.
- The backend should parse this and save the result, similar to the current `submit_pre_screening` logic.

## 2. Frontend Implementation

### 2.1. New Component: `ChatPrescreening.tsx`
- A chat interface with:
    - Message list (Agent vs. User bubbles).
    - Input field.
    - specialized UI elements (e.g., "Yes/No" buttons for quick replies).

### 2.2. Integration
- Replace the current `PreScreeningForm` in `ProtocolDetail.tsx` (or offer it as an alternative).
- Connect to the new backend endpoints.
- Handle the "Assessment Complete" state to show the final result card.

## 3. Workflow Steps

1.  **Backend Setup**:
    - Install `langchain` or `anthropic` SDK if not present.
    - Create `app/services/ai_screener.py`.
    - Update `app/api/v1/patients.py`.

2.  **Frontend Setup**:
    - Create `src/components/protocols/ChatInterface.tsx`.
    - Integrate into `ProtocolDetail.tsx`.

3.  **Testing**:
    - Verify the agent asks all required questions.
    - Verify it correctly flags ineligible users (e.g., under 18).
    - Verify it handles "I don't know" or ambiguous answers gracefully.
