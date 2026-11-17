import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Terminal, Loader2, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { AgentChatResponse, AgentToolCallLog, StudentProfile } from '../types';
import { api } from '../services/api';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  toolLogs?: AgentToolCallLog[];
}

interface CareerAgentChatProps {
  profile: StudentProfile;
}

export const CareerAgentChat: React.FC<CareerAgentChatProps> = ({ profile }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: `Hello ${profile.name.split(' ')[0]}! I am your AI Career Copilot. I use a genuine ReAct loop with 3 registered tools:\n- \`search_internships\` (retrieves real live records from our database)\n- \`analyze_skill_gap\` (evaluates your confirmed profile against requirements)\n- \`create_learning_plan\` (generates structured weekly roadmaps with verified resources)\n\nAsk me anything about matching internships or bridging your skill gaps!`
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedTraceIndex, setExpandedTraceIndex] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || inputQuery).trim();
    if (!query || isLoading) return;

    const userMessage: Message = {
      id: String(Date.now()),
      sender: 'user',
      text: query
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const res: AgentChatResponse = await api.chatWithAgent(query, profile.id);
      const assistantMessage: Message = {
        id: String(Date.now() + 1),
        sender: 'assistant',
        text: res.response,
        toolLogs: res.tool_logs
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: 'assistant',
          text: `⚠️ I encountered an error executing this request: ${err.message}`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const presetQueries = [
    'Find me Machine Learning internships and analyze my gap for the top match',
    'Analyze my skill gap for DeepCognition Labs and give me a 4-week learning plan',
    'What remote Frontend developer opportunities match React?'
  ];

  const renderMarkdown = (text: string) => {
    // Basic Markdown converter for bullet points, bolding, and links
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      let formatted = line;

      // Handle Markdown headers
      if (formatted.startsWith('### ')) {
        return <h4 key={idx} style={{ margin: '0.75rem 0 0.35rem', fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)' }}>{formatted.replace('### ', '')}</h4>;
      }
      if (formatted.startsWith('## ')) {
        return <h3 key={idx} style={{ margin: '0.85rem 0 0.4rem', fontWeight: 800, fontSize: '1.15rem', color: 'var(--text-primary)' }}>{formatted.replace('## ', '')}</h3>;
      }

      // Handle bold text **text**
      const parts = formatted.split(/(\*\*.*?\*\*)/g);
      const elements = parts.map((part, pIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={pIdx}>{part.slice(2, -2)}</strong>;
        }
        // Handle markdown link [text](url)
        const linkMatch = part.match(/\[(.*?)\]\((.*?)\)/);
        if (linkMatch) {
          const before = part.substring(0, linkMatch.index);
          const after = part.substring((linkMatch.index || 0) + linkMatch[0].length);
          return (
            <span key={pIdx}>
              {before}
              <a href={linkMatch[2]} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>
                {linkMatch[1]}
              </a>
              {after}
            </span>
          );
        }
        return part;
      });

      return <div key={idx} style={{ marginBottom: line.trim() === '' ? '0.5rem' : '0.2rem' }}>{elements}</div>;
    });
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>ReAct AI Career Copilot</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Interactive career agent powered by a multi-step ReAct reasoning loop and verified Python tools.
        </p>

        {/* Preset query suggestion pills */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
          {presetQueries.map((q, idx) => (
            <button
              key={idx}
              className="btn btn-outline"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem', borderRadius: 999 }}
              onClick={() => handleSend(q)}
              disabled={isLoading}
            >
              <Sparkles size={12} color="var(--primary)" />
              {q}
            </button>
          ))}
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`message-bubble ${m.sender === 'user' ? 'message-user' : 'message-assistant'}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.4rem', fontWeight: 700, fontSize: '0.8rem', opacity: 0.85 }}>
                {m.sender === 'user' ? (
                  <>
                    <User size={14} /> You
                  </>
                ) : (
                  <>
                    <Bot size={14} /> Career Copilot Agent
                  </>
                )}
              </div>

              {/* Tool Execution Logs Accordion (if available) */}
              {m.toolLogs && m.toolLogs.length > 0 && (
                <div style={{ marginBottom: '0.75rem' }}>
                  <button
                    onClick={() => setExpandedTraceIndex(expandedTraceIndex === m.id ? null : m.id)}
                    style={{
                      background: '#1e293b',
                      color: '#38bdf8',
                      border: 'none',
                      borderRadius: 6,
                      padding: '0.35rem 0.65rem',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.35rem'
                    }}
                  >
                    <Terminal size={12} />
                    <span>Agent ReAct Trace ({m.toolLogs.length} Tool Actions)</span>
                    {expandedTraceIndex === m.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>

                  {expandedTraceIndex === m.id && (
                    <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      {m.toolLogs.map((log, tIdx) => (
                        <div key={tIdx} className="tool-trace-card">
                          <div className="tool-trace-header">
                            <span>Step {tIdx + 1}: Action → {log.tool_name}</span>
                            <span>{log.duration_ms} ms</span>
                          </div>
                          <div style={{ color: '#94a3b8', marginBottom: '0.3rem' }}>
                            Input: {JSON.stringify(log.tool_args)}
                          </div>
                          <div style={{ color: '#a7f3d0' }}>
                            Observation: {log.observation_summary}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div>{renderMarkdown(m.text)}</div>
            </div>
          ))}

          {isLoading && (
            <div className="message-bubble message-assistant" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Loader2 size={16} className="spin-icon" color="var(--primary)" />
              <span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                ReAct Agent is reasoning and querying database tools...
              </span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-bar">
          <input
            type="text"
            className="form-input"
            placeholder="Ask about internships, analyze your skill gaps, or request a learning roadmap..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
          />
          <button
            className="btn btn-primary"
            onClick={() => handleSend()}
            disabled={isLoading || !inputQuery.trim()}
          >
            <Send size={16} />
            Send
          </button>
        </div>
      </div>
    </div>
  );
};
