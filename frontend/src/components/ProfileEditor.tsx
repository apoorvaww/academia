import React, { useState } from 'react';
import { User, Award, Briefcase, MapPin, Laptop, FileUp, Save, Check } from 'lucide-react';
import { StudentProfile, SkillEvidenceItem } from '../types';
import { api } from '../services/api';
import { ResumeUploadModal } from './ResumeUploadModal';

interface ProfileEditorProps {
  profile: StudentProfile;
  onProfileUpdated: (updated: StudentProfile) => void;
}

export const ProfileEditor: React.FC<ProfileEditorProps> = ({ profile, onProfileUpdated }) => {
  const [formData, setFormData] = useState({
    name: profile.name || '',
    email: profile.email || '',
    degree: profile.degree || '',
    major: profile.major || '',
    graduation_year: profile.graduation_year || 2026,
    target_role: profile.target_role || '',
    preferred_location: profile.preferred_location || 'Any',
    preferred_work_mode: profile.preferred_work_mode || 'remote',
    bio: profile.bio || ''
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isResumeModalOpen, setIsResumeModalOpen] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const updated = await api.updateProfile(formData, profile.id);
      onProfileUpdated(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      alert('Error updating profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemoveSkill = async (canonicalName: string) => {
    const updatedSkills = profile.skills.filter((s) => s.canonical_name !== canonicalName);
    try {
      const updated = await api.confirmSkills(updatedSkills, profile.id);
      onProfileUpdated(updated);
    } catch (err) {
      alert('Error removing skill');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Student Profile & Skill Inventory</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Manage your academic credentials, target career roles, and verified skills.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsResumeModalOpen(true)}>
          <FileUp size={16} />
          Import Resume & Extract Skills
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '1.5rem' }}>
        {/* Left Column: Profile Form */}
        <div className="card">
          <form onSubmit={handleSave}>
            <div className="card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <User size={20} color="var(--primary)" />
                <h3 className="card-title">Academic & Career Details</h3>
              </div>
              {saveSuccess && (
                <span className="badge badge-matched" style={{ display: 'flex', gap: '0.3rem' }}>
                  <Check size={12} /> Saved Successfully
                </span>
              )}
            </div>

            <div className="form-grid" style={{ marginBottom: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  name="name"
                  className="form-input"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Degree</label>
                <input
                  type="text"
                  name="degree"
                  className="form-input"
                  value={formData.degree}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Major / Specialization</label>
                <input
                  type="text"
                  name="major"
                  className="form-input"
                  value={formData.major}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Graduation Year</label>
                <input
                  type="number"
                  name="graduation_year"
                  className="form-input"
                  value={formData.graduation_year}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Target Role</label>
                <input
                  type="text"
                  name="target_role"
                  className="form-input"
                  placeholder="e.g. Machine Learning Engineer"
                  value={formData.target_role}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Work Mode Preference</label>
                <select
                  name="preferred_work_mode"
                  className="form-select"
                  value={formData.preferred_work_mode}
                  onChange={handleChange}
                >
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">On-Site</option>
                  <option value="any">Any / Flexible</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Preferred Location</label>
                <input
                  type="text"
                  name="preferred_location"
                  className="form-input"
                  placeholder="e.g. Bengaluru, Hyderabad, or Any"
                  value={formData.preferred_location}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '1.25rem' }}>
              <label className="form-label">Academic Bio / Research Interests</label>
              <textarea
                name="bio"
                className="form-textarea"
                rows={3}
                value={formData.bio}
                onChange={handleChange}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button type="submit" className="btn btn-primary" disabled={isSaving}>
                <Save size={16} />
                {isSaving ? 'Saving...' : 'Save Profile Changes'}
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Confirmed Skills */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Award size={20} color="var(--primary)" />
              <h3 className="card-title">Confirmed Skills</h3>
            </div>
            <span className="badge badge-tag">{profile.skills.length} Skills</span>
          </div>

          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            These verified skills are used by the recommendation engine and AI career agent to calculate fit scores and gaps.
          </p>

          {profile.skills.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
              <p>No confirmed skills yet.</p>
              <button
                className="btn btn-outline"
                style={{ marginTop: '0.75rem' }}
                onClick={() => setIsResumeModalOpen(true)}
              >
                Extract from Resume
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '420px', overflowY: 'auto' }}>
              {profile.skills.map((item) => (
                <div
                  key={item.canonical_name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.5rem 0.75rem',
                    background: '#f8fafc',
                    border: '1px solid var(--border-color)',
                    borderRadius: 8
                  }}
                >
                  <div>
                    <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{item.canonical_name}</span>
                    <span
                      style={{
                        marginLeft: '0.5rem',
                        fontSize: '0.7rem',
                        textTransform: 'uppercase',
                        padding: '2px 6px',
                        background: '#e0e7ff',
                        color: '#3730a3',
                        borderRadius: 4,
                        fontWeight: 700
                      }}
                    >
                      {item.proficiency || 'intermediate'}
                    </span>
                  </div>
                  <button
                    onClick={() => handleRemoveSkill(item.canonical_name)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      padding: '0 4px'
                    }}
                    title="Remove skill"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <ResumeUploadModal
        isOpen={isResumeModalOpen}
        onClose={() => setIsResumeModalOpen(false)}
        onSkillsUpdated={(updated) => onProfileUpdated(updated)}
      />
    </div>
  );
};
