import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, X, Plus, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { SkillEvidenceItem, CandidateSkill, StudentProfile } from '../types';

interface ResumeUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSkillsUpdated: (profile: StudentProfile) => void;
}

export const ResumeUploadModal: React.FC<ResumeUploadModalProps> = ({
  isOpen,
  onClose,
  onSkillsUpdated
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [rawText, setRawText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Extracted candidate skills for review
  const [candidateSkills, setCandidateSkills] = useState<CandidateSkill[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<SkillEvidenceItem[]>([]);
  const [newSkillInput, setNewSkillInput] = useState('');
  const [step, setStep] = useState<'upload' | 'review'>('upload');

  if (!isOpen) return null;

  const handleParse = async () => {
    if (!file && (!rawText || rawText.trim().length < 15)) {
      setError('Please select a PDF file or paste your resume text (min 15 chars).');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const result = await api.parseResume(file || undefined, rawText || undefined);
      setCandidateSkills(result.candidate_skills);

      // Pre-select all extracted candidate skills by default
      const initialSelected: SkillEvidenceItem[] = result.candidate_skills.map((c) => ({
        canonical_name: c.canonical_name,
        evidence_source: c.evidence_snippet,
        proficiency: 'intermediate',
        confirmation_status: 'confirmed'
      }));
      setSelectedSkills(initialSelected);
      setStep('review');
    } catch (err: any) {
      setError(err.message || 'Error parsing resume');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSkill = (skill: CandidateSkill) => {
    const exists = selectedSkills.some((s) => s.canonical_name === skill.canonical_name);
    if (exists) {
      setSelectedSkills(selectedSkills.filter((s) => s.canonical_name !== skill.canonical_name));
    } else {
      setSelectedSkills([
        ...selectedSkills,
        {
          canonical_name: skill.canonical_name,
          evidence_source: skill.evidence_snippet,
          proficiency: 'intermediate',
          confirmation_status: 'confirmed'
        }
      ]);
    }
  };

  const handleProficiencyChange = (canonicalName: string, proficiency: 'beginner' | 'intermediate' | 'advanced') => {
    setSelectedSkills(
      selectedSkills.map((s) =>
        s.canonical_name === canonicalName ? { ...s, proficiency } : s
      )
    );
  };

  const handleAddManualSkill = () => {
    if (!newSkillInput.trim()) return;
    const trimmed = newSkillInput.trim();
    if (!selectedSkills.some((s) => s.canonical_name.toLowerCase() === trimmed.toLowerCase())) {
      setSelectedSkills([
        ...selectedSkills,
        {
          canonical_name: trimmed,
          evidence_source: 'Manual Student Entry',
          proficiency: 'intermediate',
          confirmation_status: 'confirmed'
        }
      ]);
    }
    setNewSkillInput('');
  };

  const handleConfirmAndSave = async () => {
    if (selectedSkills.length === 0) {
      setError('Please select at least one skill to confirm.');
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      const updatedProfile = await api.confirmSkills(selectedSkills);
      onSkillsUpdated(updatedProfile);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save confirmed skills.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Resume Skill Extraction</h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Upload your text-based resume or paste text to extract verifiable skills.
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
            <X size={20} color="var(--text-muted)" />
          </button>
        </div>

        {error && (
          <div style={{ padding: '0.75rem 1rem', background: 'var(--danger-light)', color: 'var(--danger)', borderRadius: 8, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {step === 'upload' ? (
          <div>
            <div
              style={{
                border: '2px dashed #cbd5e1',
                borderRadius: 12,
                padding: '2rem',
                textAlign: 'center',
                backgroundColor: '#f8fafc',
                cursor: 'pointer',
                marginBottom: '1.25rem'
              }}
              onClick={() => document.getElementById('resume-file-input')?.click()}
            >
              <Upload size={36} color="var(--primary)" style={{ margin: '0 auto 0.5rem' }} />
              <p style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                {file ? file.name : 'Click to select a PDF Resume (Max 5MB)'}
              </p>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Accepts text-based .pdf format
              </p>
              <input
                id="resume-file-input"
                type="file"
                accept=".pdf,.txt"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setFile(e.target.files[0]);
                  }
                }}
              />
            </div>

            <div style={{ textAlign: 'center', margin: '0.5rem 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              — OR PASTE RESUME TEXT —
            </div>

            <textarea
              className="form-textarea"
              rows={4}
              placeholder="Paste your resume work experience, projects, or summary here..."
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              style={{ marginBottom: '1.25rem' }}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button className="btn btn-outline" onClick={onClose}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleParse} disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="spin-icon" />
                    Extracting Skills...
                  </>
                ) : (
                  <>
                    <FileText size={16} />
                    Extract Candidate Skills
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ marginBottom: '1rem', padding: '0.75rem 1rem', background: '#eff6ff', borderRadius: 8, fontSize: '0.85rem', color: '#1e40af' }}>
              <strong>Human-in-the-loop review:</strong> Select skills you confirm possessing, set your proficiency, or add custom skills before finalizing.
            </div>

            <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Extracted Skills ({candidateSkills.length} found)
            </h3>

            <div style={{ maxHeight: '280px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.6rem', paddingRight: '0.5rem', marginBottom: '1rem' }}>
              {candidateSkills.map((c) => {
                const isSelected = selectedSkills.some((s) => s.canonical_name === c.canonical_name);
                const current = selectedSkills.find((s) => s.canonical_name === c.canonical_name);
                return (
                  <div
                    key={c.canonical_name}
                    style={{
                      border: '1px solid',
                      borderColor: isSelected ? 'var(--primary)' : 'var(--border-color)',
                      backgroundColor: isSelected ? '#f5f3ff' : '#ffffff',
                      borderRadius: 8,
                      padding: '0.6rem 0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flex: 1 }}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleSkill(c)}
                        style={{ cursor: 'pointer', width: 16, height: 16 }}
                      />
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.canonical_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          Evidence: <span style={{ fontStyle: 'italic' }}>{c.evidence_snippet}</span>
                        </div>
                      </div>
                    </div>

                    {isSelected && (
                      <select
                        className="form-select"
                        style={{ width: '130px', padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
                        value={current?.proficiency || 'intermediate'}
                        onChange={(e) => handleProficiencyChange(c.canonical_name, e.target.value as any)}
                      >
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                      </select>
                    )}
                  </div>
                );
              })}
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Add additional skill (e.g. Docker, PyTorch)..."
                value={newSkillInput}
                onChange={(e) => setNewSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddManualSkill()}
              />
              <button className="btn btn-outline" onClick={handleAddManualSkill}>
                <Plus size={16} />
                Add
              </button>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button className="btn btn-outline" onClick={() => setStep('upload')}>
                Back to Upload
              </button>
              <button className="btn btn-success" onClick={handleConfirmAndSave} disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2 size={16} className="spin-icon" />
                    Saving Confirmed Skills...
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={16} />
                    Confirm {selectedSkills.length} Skills
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
