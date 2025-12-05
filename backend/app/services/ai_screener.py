import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import google.generativeai as genai

from app.models.chat import ChatSession, ChatSessionStatus
from app.models.protocol import Protocol
from app.schemas.chat import ChatMessage

class AIScreenerService:
    def __init__(self, db: Session):
        self.db = db
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
             # Fallback or error if not set, but we expect it to be set
             pass
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def start_session(self, user_id: int, protocol_id: int) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            protocol_id=protocol_id,
            history=[],
            collected_data={}
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        # Generate initial greeting
        protocol = self.db.query(Protocol).filter(Protocol.id == protocol_id).first()
        initial_message = f"Hello! I'm here to help determine if the {protocol.name} protocol is right for you. To start, could you please tell me your age?"

        self._append_message(session, "model", initial_message)
        return session

    def process_message(self, session_id: int, user_message: str) -> Dict[str, Any]:
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")

        # 1. Append user message
        self._append_message(session, "user", user_message)

        # 2. Construct chat history for Gemini
        # Gemini expects roles 'user' and 'model'
        history = []

        # Add system prompt as the first part of the context or a user message
        system_prompt = self._get_system_prompt(session)
        history.append({"role": "user", "parts": [system_prompt]})
        history.append({"role": "model", "parts": ["Understood. I will act as the medical assistant and follow your instructions."]})

        for m in session.history:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        # 3. Call Gemini
        chat = self.model.start_chat(history=history)
        response = chat.send_message(user_message) # This might be redundant if we already added user_message to history?
        # Actually, start_chat takes history *before* the new message.
        # So I should NOT add the current user_message to the history list passed to start_chat.
        # Let's fix the logic:

        # Re-construct history excluding the last user message (which we just appended to DB)
        history_for_api = []
        history_for_api.append({"role": "user", "parts": [system_prompt]})
        history_for_api.append({"role": "model", "parts": ["Understood. I will act as the medical assistant and follow your instructions."]})

        # Add all previous messages (excluding the one we just added to DB)
        # Actually, let's just use the chat object properly.
        # We can just send the whole history + new message as a generate_content call if we want statelessness,
        # or use start_chat.

        # Let's use generate_content with full context for simplicity and control
        full_prompt = []
        full_prompt.append({"role": "user", "parts": [system_prompt]})
        full_prompt.append({"role": "model", "parts": ["Understood. I will act as the medical assistant."]})

        for m in session.history: # Includes the new user message
            role = "user" if m["role"] == "user" else "model"
            full_prompt.append({"role": role, "parts": [m["content"]]})

        response = self.model.generate_content(full_prompt)

        ai_response_text = response.text

        # 4. Parse response
        eligibility_result = None

        if "<result>" in ai_response_text:
            try:
                start = ai_response_text.find("<result>") + len("<result>")
                end = ai_response_text.find("</result>")
                json_str = ai_response_text[start:end].strip()
                eligibility_result = json.loads(json_str)

                ai_response_text = ai_response_text.replace(f"<result>{json_str}</result>", "").strip()
                ai_response_text = ai_response_text.replace("<result>", "").replace("</result>", "").strip() # Cleanup

                session.status = ChatSessionStatus.COMPLETED
                session.collected_data = eligibility_result
                self.db.commit()
            except Exception as e:
                print(f"Error parsing AI result: {e}")

        # 5. Append AI response
        self._append_message(session, "model", ai_response_text)

        return {
            "response": ai_response_text,
            "status": session.status,
            "eligibility_result": eligibility_result
        }

    def _append_message(self, session: ChatSession, role: str, content: str):
        history = list(session.history)
        # Map 'model' to 'assistant' for frontend compatibility if needed,
        # but let's keep it consistent in DB.
        # Frontend expects 'assistant'.
        db_role = "assistant" if role == "model" else "user"
        history.append({"role": db_role, "content": content})
        session.history = history
        session.updated_at = datetime.utcnow()
        self.db.commit()

    def _get_system_prompt(self, session: ChatSession) -> str:
        protocol = self.db.query(Protocol).filter(Protocol.id == session.protocol_id).first()

        return f"""You are a compassionate and professional medical assistant for a clinic offering {protocol.name}.
Your goal is to screen patients for eligibility.

Required Information to Collect:
1. Age (Must be >= 18)
2. Medical History (specifically ask about heart conditions, psychosis, bipolar disorder)
3. Current Medications (specifically ask about MAOIs)

Rules:
- Ask ONE question at a time. Do not overwhelm the user.
- Be polite and empathetic.
- If the user is under 18, politely inform them they are not eligible.
- If the user reports psychosis or bipolar disorder, they are likely ineligible (risk level: excluded).
- If the user reports heart conditions or MAOIs, they are high risk.

Output Format:
- Converse naturally with the user.
- WHEN you have collected all necessary information OR if you determine they are ineligible early (e.g., under 18), append a JSON block wrapped in <result> tags to your response.
- The JSON should look like this:
<result>
{{
  "eligible": boolean,
  "risk_level": "low" | "medium" | "high" | "excluded",
  "contraindications": ["list", "of", "reasons"],
  "recommendations": ["list", "of", "next", "steps"],
  "collected_data": {{ "age": 25, "medical_history": "...", "medications": "..." }}
}}
</result>

Do not show the <result> block to the user in your text, just append it for the system to process.
"""
