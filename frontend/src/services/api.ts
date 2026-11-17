import {
  StudentProfile,
  ResumeParseResponse,
  SkillEvidenceItem,
  RecommendationsResponse,
  Internship,
  SkillGapResponse,
  LearningPlanResponse,
  AgentChatResponse,
  HealthResponse
} from '../types';

const API_BASE = '/api';

export const api = {
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getProfile(studentId: number = 1): Promise<StudentProfile> {
    const res = await fetch(`${API_BASE}/profile?student_id=${studentId}`);
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async updateProfile(data: Partial<StudentProfile>, studentId: number = 1): Promise<StudentProfile> {
    const res = await fetch(`${API_BASE}/profile?student_id=${studentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update profile');
    return res.json();
  },

  async parseResume(file?: File, rawText?: string): Promise<ResumeParseResponse> {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (rawText) {
      formData.append('raw_text', rawText);
    }

    const res = await fetch(`${API_BASE}/profile/resume/parse`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Resume parsing failed' }));
      throw new Error(err.detail || 'Resume parsing failed');
    }
    return res.json();
  },

  async confirmSkills(skills: SkillEvidenceItem[], studentId: number = 1): Promise<StudentProfile> {
    const res = await fetch(`${API_BASE}/profile/skills/confirm?student_id=${studentId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ skills })
    });
    if (!res.ok) throw new Error('Failed to confirm skills');
    return res.json();
  },

  async getRecommendations(studentId: number = 1, limit: number = 10): Promise<RecommendationsResponse> {
    const res = await fetch(`${API_BASE}/internships/recommendations?student_id=${studentId}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch recommendations');
    return res.json();
  },

  async getInternship(id: number): Promise<Internship> {
    const res = await fetch(`${API_BASE}/internships/${id}`);
    if (!res.ok) throw new Error('Failed to fetch internship details');
    return res.json();
  },

  async getSkillGap(internshipId: number, studentId: number = 1): Promise<SkillGapResponse> {
    const res = await fetch(`${API_BASE}/skill-gap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ internship_id: internshipId, student_id: studentId })
    });
    if (!res.ok) throw new Error('Failed to calculate skill gap');
    return res.json();
  },

  async getLearningPlan(missingSkills: string[], targetRole: string, timeBudgetWeeks: number = 4): Promise<LearningPlanResponse> {
    const res = await fetch(`${API_BASE}/learning-plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        missing_skills: missingSkills,
        target_role: targetRole,
        time_budget_weeks: timeBudgetWeeks
      })
    });
    if (!res.ok) throw new Error('Failed to generate learning plan');
    return res.json();
  },

  async chatWithAgent(query: string, studentId: number = 1): Promise<AgentChatResponse> {
    const res = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, student_id: studentId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Agent query failed' }));
      throw new Error(err.detail || 'Agent query failed');
    }
    return res.json();
  }
};
