import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from anthropic import Anthropic

from app.models.chat import ChatSession, ChatSessionStatus
from app.models.protocol import Protocol
from app.schemas.chat import ChatMessage

class AIScreenerService:
    def __init__(self, db: Session):
        self.db = db
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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

        self._append_message(session, "assistant", initial_message)
        return session

    def process_message(self, session_id: int, user_message: str) -> Dict[str, Any]:
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")

        # 1. Append user message
        self._append_message(session, "user", user_message)

        # 2. Construct prompt for LLM
        system_prompt = self._get_system_prompt(session)
        messages = [{"role": m["role"], "content": m["content"]} for m in session.history]

        # 3. Call LLM
        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )

        ai_response_text = response.content[0].text

        # 4. Parse response (expecting JSON or structured text if we asked for it,
        # but for simplicity, let's assume the LLM replies naturally and we extract data separately
        # OR we ask the LLM to output a specific format for data extraction).

        # For this MVP, let's use a simpler approach:
        # The system prompt will instruct the AI to output a special JSON block ONLY when it has collected enough data
        # or determined ineligibility. Otherwise, it just chats.

        eligibility_result = None

        if "<result>" in ai_response_text:
            # Extract the JSON result
            try:
                start = ai_response_text.find("<result>") + len("<result>")
                end = ai_response_text.find("</result>")
                json_str = ai_response_text[start:end].strip()
                eligibility_result = json.loads(json_str)

                # Clean the response to show to user (remove the hidden block)
                ai_response_text = ai_response_text.replace(f"<result>{json_str}</result>", "").strip()

                # Update session status
                session.status = ChatSessionStatus.COMPLETED
                session.collected_data = eligibility_result
                self.db.commit()
            except Exception as e:
                print(f"Error parsing AI result: {e}")

        # 5. Append AI response
        self._append_message(session, "assistant", ai_response_text)

        return {
            "response": ai_response_text,
            "status": session.status,
            "eligibility_result": eligibility_result
        }

    def _append_message(self, session: ChatSession, role: str, content: str):
        # SQLAlchemy JSON mutation tracking can be tricky, so we copy, append, and reassign
        history = list(session.history)
        history.append({"role": role, "content": content})
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
