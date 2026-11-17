export interface SkillEvidenceItem {
  canonical_name: string;
  evidence_source?: string;
  proficiency?: 'beginner' | 'intermediate' | 'advanced';
  confirmation_status?: 'confirmed' | 'candidate';
}

export interface StudentProfile {
  id: number;
  name: string;
  email: string;
  degree?: string;
  major?: string;
  graduation_year?: number;
  target_role?: string;
  preferred_location?: string;
  preferred_work_mode?: string;
  bio?: string;
  skills: SkillEvidenceItem[];
}

export interface CandidateSkill {
  canonical_name: string;
  matched_term: string;
  evidence_snippet: string;
  category: string;
}

export interface ResumeParseResponse {
  detected_name?: string;
  detected_email?: string;
  candidate_skills: CandidateSkill[];
  text_preview: string;
}

export interface Internship {
  id: number;
  title: string;
  company: string;
  location: string;
  work_mode: string;
  description: string;
  required_skills: string[];
  preferred_skills: string[];
  status: string;
  source_label: string;
}

export interface FitScoreBreakdown {
  semantic_score: number;
  skill_score: number;
  preference_score: number;
  fit_score: number;
  fit_percentage: number;
  matched_required_skills: string[];
  missing_required_skills: string[];
  matched_preferred_skills: string[];
  explanation: string;
}

export interface RecommendationItem {
  internship: Internship;
  score_breakdown: FitScoreBreakdown;
}

export interface RecommendationsResponse {
  student_id: number;
  count: number;
  recommendations: RecommendationItem[];
}

export interface SkillGapResponse {
  internship_id: number;
  internship_title: string;
  company: string;
  matched_required_skills: string[];
  missing_required_skills: string[];
  matched_preferred_skills: string[];
  missing_preferred_skills: string[];
  readiness_level: string;
  explanation: string;
}

export interface LearningResourceItem {
  title: string;
  url: string;
  skill_tag: string;
  resource_type: string;
  description?: string;
  is_verified: boolean;
}

export interface LearningPlanStep {
  week_number: number;
  skill: string;
  action_item: string;
  practice_project: string;
  resources: LearningResourceItem[];
}

export interface LearningPlanResponse {
  target_role: string;
  total_weeks: number;
  skills_addressed: string[];
  steps: LearningPlanStep[];
  summary_guidance: string;
}

export interface AgentToolCallLog {
  tool_name: string;
  tool_args: Record<string, any>;
  observation_summary: string;
  duration_ms?: number;
}

export interface AgentChatResponse {
  response: string;
  tool_logs: AgentToolCallLog[];
  grounded_evidence: Record<string, any>;
}

export interface HealthResponse {
  status: string;
  semantic_embedder: string;
  llm_provider: string;
  version: string;
}
