import React, { useState } from 'react';
import { AssistantResponse } from '../types';
import { MessageSquare, X, Send, Play, BookOpen } from 'lucide-react';

interface AssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onTriggerSimulation?: (config: any) => void;
}

export const AssistantDrawer: React.FC<AssistantDrawerProps> = ({
  isOpen,
  onClose,
  onTriggerSimulation,
}) => {
  const [inputMessage, setInputMessage] = useState<string>('');
  const [messages, setMessages] = useState<
    Array<{ sender: 'user' | 'assistant'; text: string; response?: AssistantResponse }>
  >([
    {
      sender: 'assistant',
      text: "AdaptiveGrover-QCA Research Assistant ready. Ask questions regarding empirical scaling, noise crossover thresholds, AES readiness, or formulate simulation runs.",
    },
  ]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const quickPrompts = [
    "Can quantum computers break AES-128?",
    "What is the noise crossover threshold?",
    "Explain the fair filtering baseline",
    "Simulate adaptive Grover on 6 bits with 2% noise",
  ];

  const handleSend = async (msgText: string, confirmed: boolean = false) => {
    if (!msgText.trim() && !confirmed) return;

    if (!confirmed) {
      setMessages((prev) => [...prev, { sender: 'user', text: msgText }]);
      setInputMessage('');
    }

    setIsLoading(true);
    try {
      const history = messages.map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

      const res = await fetch("/api/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msgText,
          conversation_history: history,
          confirmed_execution: confirmed,
        }),
      });

      if (!res.ok) throw new Error(`Assistant error: ${res.status}`);
      const data: AssistantResponse = await res.json();

      setMessages((prev) => [
        ...prev,
        { sender: 'assistant', text: data.reply, response: data },
      ]);

      if (confirmed && data.extracted_config && onTriggerSimulation) {
        onTriggerSimulation(data.extracted_config);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `Request failed: ${err.message || 'Unable to reach assistant backend.'}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-96 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-xl z-40 flex flex-col">
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <span className="font-semibold text-sm text-slate-800 dark:text-slate-200">
            Research Assistant
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`p-3 rounded-xl max-w-[90%] whitespace-pre-wrap leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700'
              }`}
            >
              {m.text}

              {m.response?.requires_confirmation && m.response.extracted_config && (
                <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                  <div className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    Confirmation Protocol Required
                  </div>
                  <button
                    onClick={() => handleSend(m.text, true)}
                    className="w-full flex items-center justify-center py-1.5 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-[11px] shadow-xs"
                  >
                    <Play className="w-3 h-3 mr-1.5" />
                    Confirm & Execute Simulation
                  </button>
                </div>
              )}

              {m.response?.grounded_evidence && m.response.grounded_evidence.length > 0 && (
                <div className="mt-2.5 pt-2 border-t border-slate-200 dark:border-slate-700/60 text-[10px] text-slate-500 dark:text-slate-400 space-y-1">
                  <span className="font-semibold uppercase tracking-wider block">Grounded Evidence:</span>
                  {m.response.grounded_evidence.map((ev, i) => (
                    <div key={i} className="flex items-start space-x-1">
                      <BookOpen className="w-3 h-3 text-purple-500 mt-0.5 shrink-0" />
                      <span>{ev}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="text-xs text-slate-400 italic">Assistant is evaluating request...</div>
        )}
      </div>

      <div className="p-3 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">
        <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-2">
          Suggested Queries:
        </div>
        <div className="flex flex-wrap gap-1.5">
          {quickPrompts.map((q, i) => (
            <button
              key={i}
              onClick={() => handleSend(q, false)}
              className="text-[11px] px-2 py-1 rounded-md bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-emerald-500 text-left truncate max-w-full"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      <div className="p-3 border-t border-slate-200 dark:border-slate-800 flex items-center space-x-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend(inputMessage, false)}
          placeholder="Ask research questions or simulate..."
          className="flex-1 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-2 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
        />
        <button
          onClick={() => handleSend(inputMessage, false)}
          disabled={!inputMessage.trim() || isLoading}
          className="p-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
