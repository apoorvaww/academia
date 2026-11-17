import React from 'react';
import { Compass, User, Briefcase, Bot } from 'lucide-react';
import { HealthResponse } from '../types';

interface NavbarProps {
  activeTab: 'profile' | 'recommendations' | 'agent';
  setActiveTab: (tab: 'profile' | 'recommendations' | 'agent') => void;
  health: HealthResponse | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, health }) => {
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <Compass size={22} />
        </div>
        <div>
          <h1 className="brand-title">Academia–Industry Portal</h1>
          <p className="brand-subtitle">Skill Mapping • Recommendations • ReAct Career Copilot</p>
        </div>
      </div>

      <nav className="nav-tabs">
        <button
          className={`nav-tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <User size={16} />
          Profile & Skills
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          <Briefcase size={16} />
          Internship Matches
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'agent' ? 'active' : ''}`}
          onClick={() => setActiveTab('agent')}
        >
          <Bot size={16} />
          AI Career Copilot
        </button>
      </nav>

      <div>
        {health ? (
          <div className="system-status-badge" title={`Embedder: ${health.semantic_embedder} | LLM: ${health.llm_provider}`}>
            <span className="status-dot"></span>
            <span>Agent & Engine Online</span>
          </div>
        ) : (
          <div className="system-status-badge" style={{ background: '#fef3c7', color: '#92400e', borderColor: '#fde68a' }}>
            <span>Connecting...</span>
          </div>
        )}
      </div>
    </header>
  );
};
