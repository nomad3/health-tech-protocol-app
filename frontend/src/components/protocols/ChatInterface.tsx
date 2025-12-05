import { Bot, Loader2, Send } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import api from '../../services/api';
import type { ChatMessage, ChatMessageResponse, ChatSessionResponse } from '../../types/chat';

interface ChatInterfaceProps {
  protocolId: number;
  onComplete: (result: any) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ protocolId, onComplete }) => {
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    startSession();
  }, [protocolId]);

  const startSession = async () => {
    try {
      setIsLoading(true);
      const response = await api.post<ChatSessionResponse>(`/api/v1/patients/protocols/${protocolId}/chat/start`);
      setSessionId(response.data.session_id);
      setMessages(response.data.history);
    } catch (error) {
      console.error("Failed to start chat session:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMsg: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.post<ChatMessageResponse>(`/api/v1/patients/chat/${sessionId}/message`, {
        session_id: sessionId,
        message: userMsg.content
      });

      const aiMsg: ChatMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, aiMsg]);

      if (response.data.status === 'completed' && response.data.eligibility_result) {
        onComplete(response.data.eligibility_result);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-200 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
          <Bot className="w-6 h-6 text-indigo-600" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">AI Medical Assistant</h3>
          <p className="text-sm text-gray-500">Pre-screening Interview</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-none'
                  : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-sm'
                }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none p-4 shadow-sm flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
              <span className="text-sm text-gray-500">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your answer..."
            className="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="p-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
