import React from 'react';
import { X, CheckCircle, AlertTriangle, BookOpen, Layers } from 'lucide-react';
import { SkillGapResponse } from '../types';

interface SkillGapModalProps {
  gap: SkillGapResponse | null;
  onClose: () => void;
  onRequestLearningPlan: (missingSkills: string[], targetRole: string) => void;
}

export const SkillGapModal: React.FC<SkillGapModalProps> = ({
  gap,
  onClose,
  onRequestLearningPlan
}) => {
  if (!gap) return null;

  const getReadinessBadge = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
        return <span className="badge badge-matched">High Readiness</span>;
      case 'moderate':
        return <span className="badge badge-preferred">Moderate Readiness</span>;
      default:
        return <span className="badge badge-missing">Needs Preparation</span>;
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
              <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Skill Gap Analysis</h2>
              {getReadinessBadge(gap.readiness_level)}
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              {gap.internship_title} at <strong>{gap.company}</strong>
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
            <X size={20} color="var(--text-muted)" />
          </button>
        </div>

        <div style={{ padding: '0.85rem 1rem', background: '#f8fafc', border: '1px solid var(--border-color)', borderRadius: 10, marginBottom: '1.25rem' }}>
          <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            Actionable Guidance:
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>{gap.explanation}</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
          {/* Matched Skills */}
          <div style={{ border: '1px solid #d1fae5', background: '#f0fdf4', borderRadius: 10, padding: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#065f46', fontWeight: 700, fontSize: '0.88rem', marginBottom: '0.5rem' }}>
              <CheckCircle size={16} />
              Matched Required Skills ({gap.matched_required_skills.length})
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {gap.matched_required_skills.length === 0 ? (
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None matched yet</span>
              ) : (
                gap.matched_required_skills.map((s) => (
                  <span key={s} className="badge badge-matched">
                    {s}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Missing Skills */}
          <div style={{ border: '1px solid #fee2e2', background: '#fef2f2', borderRadius: 10, padding: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#991b1b', fontWeight: 700, fontSize: '0.88rem', marginBottom: '0.5rem' }}>
              <AlertTriangle size={16} />
              Missing Required Skills ({gap.missing_required_skills.length})
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {gap.missing_required_skills.length === 0 ? (
                <span style={{ fontSize: '0.8rem', color: '#065f46' }}>✓ All required skills met!</span>
              ) : (
                gap.missing_required_skills.map((s) => (
                  <span key={s} className="badge badge-missing">
                    {s}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Preferred skills breakdown */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
            Preferred / Bonus Skills
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {gap.matched_preferred_skills.map((s) => (
              <span key={s} className="badge badge-preferred">
                ✓ {s} (Bonus Matched)
              </span>
            ))}
            {gap.missing_preferred_skills.map((s) => (
              <span key={s} className="badge badge-tag">
                {s}
              </span>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
          <button className="btn btn-outline" onClick={onClose}>
            Close
          </button>
          {gap.missing_required_skills.length > 0 && (
            <button
              className="btn btn-primary"
              onClick={() => {
                onRequestLearningPlan(gap.missing_required_skills, gap.internship_title);
                onClose();
              }}
            >
              <BookOpen size={16} />
              Build Learning Plan for Missing Skills
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
