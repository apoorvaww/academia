import React, { useState } from 'react';
import { Briefcase, MapPin, Building, ChevronDown, ChevronUp, Sparkles, AlertCircle, Layers } from 'lucide-react';
import { RecommendationItem, StudentProfile, SkillGapResponse, LearningPlanResponse } from '../types';
import { api } from '../services/api';
import { SkillGapModal } from './SkillGapModal';
import { LearningPlanModal } from './LearningPlanModal';

interface RecommendationListProps {
  recommendations: RecommendationItem[];
  profile: StudentProfile;
  isLoading: boolean;
  onRefresh: () => void;
}

export const RecommendationList: React.FC<RecommendationListProps> = ({
  recommendations,
  profile,
  isLoading,
  onRefresh
}) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [activeGap, setActiveGap] = useState<SkillGapResponse | null>(null);
  const [activePlan, setActivePlan] = useState<LearningPlanResponse | null>(null);
  const [isGapLoading, setIsGapLoading] = useState(false);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleInspectGap = async (internshipId: number) => {
    setIsGapLoading(true);
    try {
      const gap = await api.getSkillGap(internshipId, profile.id);
      setActiveGap(gap);
    } catch (err) {
      alert('Failed to calculate skill gap.');
    } finally {
      setIsGapLoading(false);
    }
  };

  const handleRequestLearningPlan = async (missingSkills: string[], targetRole: string) => {
    try {
      const plan = await api.getLearningPlan(missingSkills, targetRole, 4);
      setActivePlan(plan);
    } catch (err) {
      alert('Failed to generate learning plan.');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Curated Internship Matches</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Hybrid ranking combining Sentence Transformers FAISS retrieval (60%), weighted skill overlap (30%), and preferences (10%).
          </p>
        </div>
        <button className="btn btn-outline" onClick={onRefresh} disabled={isLoading}>
          <Sparkles size={16} color="var(--primary)" />
          {isLoading ? 'Computing Matches...' : 'Refresh Matches'}
        </button>
      </div>

      {recommendations.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
          <AlertCircle size={36} color="var(--text-muted)" style={{ margin: '0 auto 0.75rem' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.4rem' }}>No Matches Found</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Ensure you have added skills to your profile or click "Refresh Matches".
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {recommendations.map((item, index) => {
            const { internship, score_breakdown } = item;
            const isExpanded = expandedId === internship.id;

            return (
              <div key={internship.id} className="card" style={{ marginBottom: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
                      <span className="badge badge-tag" style={{ fontWeight: 700 }}>
                        #{index + 1}
                      </span>
                      <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {internship.title}
                      </h3>
                      <span className="badge badge-sample">{internship.source_label}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Building size={14} />
                        {internship.company}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <MapPin size={14} />
                        {internship.location} ({internship.work_mode})
                      </span>
                    </div>

                    <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '0.85rem' }}>
                      {internship.description}
                    </p>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        REQUIRED SKILLS:
                      </span>
                      {score_breakdown.matched_required_skills.map((s) => (
                        <span key={s} className="badge badge-matched">
                          ✓ {s}
                        </span>
                      ))}
                      {score_breakdown.missing_required_skills.map((s) => (
                        <span key={s} className="badge badge-missing">
                          ✗ {s}
                        </span>
                      ))}
                      {score_breakdown.matched_preferred_skills.map((s) => (
                        <span key={s} className="badge badge-preferred">
                          + {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Fit Score Badge Column */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', minWidth: '150px' }}>
                    <div className="fit-score-box">
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                          Fit Score
                        </div>
                        <div className="fit-percentage-value">
                          {score_breakdown.fit_percentage}%
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                      <button
                        className="btn btn-primary"
                        style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
                        onClick={() => handleInspectGap(internship.id)}
                        disabled={isGapLoading}
                      >
                        <Layers size={14} />
                        Skill Gap
                      </button>
                      <button
                        className="btn btn-outline"
                        style={{ padding: '0.4rem 0.6rem', fontSize: '0.8rem' }}
                        onClick={() => toggleExpand(internship.id)}
                      >
                        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Expandable Explanation Breakdown */}
                {isExpanded && (
                  <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
                    <div style={{ fontWeight: 700, marginBottom: '0.4rem', color: 'var(--text-primary)' }}>
                      Ranking Formula Breakdown:
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', marginBottom: '0.75rem' }}>
                      <div style={{ padding: '0.6rem 0.8rem', background: '#f8fafc', borderRadius: 8, border: '1px solid var(--border-color)' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Semantic Relevance (60%)</div>
                        <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--primary)' }}>
                          {(score_breakdown.semantic_score * 100).toFixed(1)}%
                        </div>
                      </div>

                      <div style={{ padding: '0.6rem 0.8rem', background: '#f8fafc', borderRadius: 8, border: '1px solid var(--border-color)' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Weighted Skill Overlap (30%)</div>
                        <div style={{ fontWeight: 700, fontSize: '1rem', color: '#059669' }}>
                          {(score_breakdown.skill_score * 100).toFixed(1)}%
                        </div>
                      </div>

                      <div style={{ padding: '0.6rem 0.8rem', background: '#f8fafc', borderRadius: 8, border: '1px solid var(--border-color)' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Preference Alignment (10%)</div>
                        <div style={{ fontWeight: 700, fontSize: '1rem', color: '#d97706' }}>
                          {(score_breakdown.preference_score * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>

                    <div style={{ padding: '0.6rem 0.8rem', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 8, color: '#166534' }}>
                      <strong>Explainability:</strong> {score_breakdown.explanation}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <SkillGapModal
        gap={activeGap}
        onClose={() => setActiveGap(null)}
        onRequestLearningPlan={handleRequestLearningPlan}
      />

      <LearningPlanModal
        plan={activePlan}
        onClose={() => setActivePlan(null)}
      />
    </div>
  );
};
