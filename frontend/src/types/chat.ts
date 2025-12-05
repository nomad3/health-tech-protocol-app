export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatSessionResponse {
  session_id: number;
  protocol_id: number;
  status: string;
  created_at: string;
  history: ChatMessage[];
}

export interface ChatMessageResponse {
  response: string;
  session_id: number;
  status: string;
  eligibility_result?: {
    eligible: boolean;
    risk_level: string;
    contraindications: string[];
    recommendations: string[];
    collected_data: any;
  };
}
