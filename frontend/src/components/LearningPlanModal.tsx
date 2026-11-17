import React from 'react';
import { X, Calendar, ExternalLink, Code2, CheckSquare } from 'lucide-react';
import { LearningPlanResponse } from '../types';

interface LearningPlanModalProps {
  plan: LearningPlanResponse | null;
  onClose: () => void;
}

export const LearningPlanModal: React.FC<LearningPlanModalProps> = ({ plan, onClose }) => {
  if (!plan) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '780px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 700 }}>Structured Learning Plan</h2>
              <span className="badge badge-preferred" style={{ display: 'flex', gap: '0.3rem' }}>
                <Calendar size={12} /> {plan.total_weeks} Weeks Roadmap
              </span>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Tailored preparation curriculum for <strong>{plan.target_role}</strong>
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
            <X size={20} color="var(--text-muted)" />
          </button>
        </div>

        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          {plan.summary_guidance}
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
          {plan.steps.map((step, idx) => (
            <div
              key={idx}
              style={{
                border: '1px solid var(--border-color)',
                borderRadius: 12,
                padding: '1.1rem',
                background: '#ffffff',
                boxShadow: 'var(--shadow-sm)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span
                    style={{
                      background: 'var(--primary-light)',
                      color: 'var(--primary)',
                      padding: '2px 8px',
                      borderRadius: 6,
                      fontWeight: 700,
                      fontSize: '0.8rem'
                    }}
                  >
                    WEEK {step.week_number}
                  </span>
                  <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
                    {step.skill}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.4rem', fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '0.6rem' }}>
                <CheckSquare size={16} color="var(--primary)" style={{ flexShrink: 0, marginTop: 2 }} />
                <span>{step.action_item}</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.4rem', fontSize: '0.88rem', color: '#065f46', background: 'var(--success-light)', padding: '0.5rem 0.75rem', borderRadius: 8, marginBottom: '0.75rem' }}>
                <Code2 size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                <span><strong>Hands-on Capstone:</strong> {step.practice_project}</span>
              </div>

              {step.resources.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                    VERIFIED CURATED RESOURCES:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {step.resources.map((res, rIdx) => (
                      <a
                        key={rIdx}
                        href={res.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          textDecoration: 'none',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          background: '#f1f5f9',
                          color: '#1e293b',
                          padding: '0.35rem 0.65rem',
                          borderRadius: 6,
                          fontSize: '0.78rem',
                          fontWeight: 500,
                          border: '1px solid #cbd5e1'
                        }}
                      >
                        <span>{res.title}</span>
                        <ExternalLink size={12} color="var(--primary)" />
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn btn-primary" onClick={onClose}>
            Got it, Let's Learn!
          </button>
        </div>
      </div>
    </div>
  );
};
