import React, { useState, useEffect, useRef } from 'react';
import { Bot, User, Send, Trash2, Sparkles, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../api/client';
import type { ChatMessage, AIStatus } from '../types';

export const AI: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      role: 'assistant',
      content:
        'Hello! I am your AI Expense Assistant. I analyze your SQLite database, compute ML predictions, and generate grounded financial insights. Ask me anything!',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [openSources, setOpenSources] = useState<Record<string, boolean>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    api.ai.getStatus().then(setAiStatus).catch(console.error);
  }, []);

  const starterPrompts = [
    'How much did I spend this month?',
    'What category costs me the most?',
    'How much did I spend last week?',
    'Did I have any unusual expenses?',
    'What are my recurring expenses?',
    'How much am I likely to spend next month?',
    'What if I reduce Shopping spending by 20%?',
    'Give me a complete spending analysis.',
  ];

  const handleSendMessage = async (queryText?: string) => {
    const text = queryText || input;
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput('');
    setLoading(true);

    try {
      const response = await api.ai.chat(text);
      const assistantMsg: ChatMessage = {
        id: `ast-${Date.now()}`,
        role: 'assistant',
        content: response.reply,
        tool_calls: response.tool_calls,
        mode: response.mode,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `I encountered an error connecting to the backend AI engine: ${err.message}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 'init-reset',
        role: 'assistant',
        content: 'Conversation history cleared. How can I help you next?',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  const toggleSources = (id: string) => {
    setOpenSources((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] space-y-4">
      {/* Header Banner */}
      <div className="flex items-center justify-between px-6 py-4 glass-panel shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-blue-600 text-white shadow-md shadow-blue-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-base text-slate-900 dark:text-white">Ask Expense AI</h2>
            <p className="text-xs text-slate-500">Grounded tool calling over SQLite transactions & ML intelligence.</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span
            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
              aiStatus?.mode === 'ONLINE'
                ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full mr-2 ${
                aiStatus?.mode === 'ONLINE' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
              }`}
            />
            {aiStatus?.mode === 'ONLINE' ? `Ollama (${aiStatus.model_name})` : 'Smart Tool Engine'}
          </span>

          <button
            onClick={handleClearChat}
            className="p-2 rounded-xl text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Clear Chat History"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chat Messages Container */}
      <div className="flex-1 glass-panel p-6 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start space-x-3 ${
              msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                msg.role === 'user'
                  ? 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900'
                  : 'bg-blue-600 text-white'
              }`}
            >
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`max-w-2xl space-y-1 ${msg.role === 'user' ? 'text-right' : ''}`}>
              <div
                className={`p-4 rounded-2xl text-xs whitespace-pre-wrap leading-relaxed inline-block text-left ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-800/90 text-slate-900 dark:text-slate-100 border border-slate-200/60 dark:border-slate-700/50'
                }`}
              >
                {msg.content}
              </div>

              {/* Grounded Tool Sources Callout Accordion */}
              {msg.tool_calls && msg.tool_calls.length > 0 && (
                <div className="pt-1 text-left">
                  <button
                    onClick={() => toggleSources(msg.id)}
                    className="inline-flex items-center space-x-1 text-[10px] font-semibold text-slate-500 dark:text-slate-400 hover:text-blue-600"
                  >
                    <ShieldCheck className="w-3 h-3 text-emerald-500" />
                    <span>Grounded Sources ({msg.tool_calls.length} tool calls executed)</span>
                    {openSources[msg.id] ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>

                  {openSources[msg.id] && (
                    <div className="mt-1 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[10px] space-y-1 font-mono">
                      {msg.tool_calls.map((tc, idx) => (
                        <div key={idx} className="text-slate-600 dark:text-slate-400">
                          <span className="font-bold text-blue-600 dark:text-blue-400">• {tc.tool_name}</span>(
                          {JSON.stringify(tc.arguments)})
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <span className="text-[10px] text-slate-400 px-1 block">{msg.timestamp}</span>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-slate-400 text-xs">
            <div className="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center">
              <Bot className="w-4 h-4 animate-bounce" />
            </div>
            <div className="p-3 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-500 font-medium">
              Evaluating intelligence tools and querying database...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Starter Chips */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 shrink-0">
        <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
        {starterPrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => handleSendMessage(prompt)}
            className="px-3 py-1.5 rounded-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-blue-500 text-slate-700 dark:text-slate-300 text-xs font-medium whitespace-nowrap shadow-2xs transition-colors shrink-0"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
        className="flex items-center space-x-3 shrink-0"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question (e.g., How much did I spend last week?)"
          className="flex-1 px-4 py-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white text-xs outline-none focus:border-blue-500 shadow-sm"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-3 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 transition-colors shadow-sm"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
