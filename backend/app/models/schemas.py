from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# --- Skill Schemas ---
class SkillBase(BaseModel):
    canonical_name: str
    category: Optional[str] = "Technical"

class SkillEvidenceItem(BaseModel):
    canonical_name: str
    evidence_source: Optional[str] = None
    proficiency: Optional[str] = "intermediate"
    confirmation_status: Optional[str] = "confirmed"

class SkillConfirmationRequest(BaseModel):
    skills: List[SkillEvidenceItem]

# --- Student Profile Schemas ---
class StudentProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    degree: Optional[str] = "B.Tech Computer Science"
    major: Optional[str] = "Computer Science"
    graduation_year: Optional[int] = 2026
    target_role: Optional[str] = "Machine Learning Engineer"
    preferred_location: Optional[str] = "Any"
    preferred_work_mode: Optional[str] = "remote"  # remote, hybrid, onsite, any
    bio: Optional[str] = ""
    skills: Optional[List[SkillEvidenceItem]] = []

class StudentProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    target_role: Optional[str] = None
    preferred_location: Optional[str] = None
    preferred_work_mode: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[SkillEvidenceItem]] = None

class StudentProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    degree: Optional[str]
    major: Optional[str]
    graduation_year: Optional[int]
    target_role: Optional[str]
    preferred_location: Optional[str]
    preferred_work_mode: Optional[str]
    bio: Optional[str]
    skills: List[SkillEvidenceItem] = []

    model_config = ConfigDict(from_attributes=True)

# --- Resume Parsing ---
class CandidateSkill(BaseModel):
    canonical_name: str
    matched_term: str
    evidence_snippet: str
    category: str

class ResumeParseResponse(BaseModel):
    detected_name: Optional[str] = None
    detected_email: Optional[str] = None
    candidate_skills: List[CandidateSkill] = []
    text_preview: str

# --- Internship & Recommendations ---
class InternshipResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    work_mode: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    status: str
    source_label: str

    model_config = ConfigDict(from_attributes=True)

class FitScoreBreakdown(BaseModel):
    semantic_score: float = Field(..., description="Cosine similarity score (0.0 - 1.0)")
    skill_score: float = Field(..., description="Weighted skill overlap score (0.0 - 1.0)")
    preference_score: float = Field(..., description="Work mode and role alignment score (0.0 - 1.0)")
    fit_score: float = Field(..., description="Combined weighted score: 0.6*sem + 0.3*skill + 0.1*pref")
    fit_percentage: int = Field(..., description="Fit score represented as integer percentage (0-100%)")
    matched_required_skills: List[str] = []
    missing_required_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    explanation: str

class RecommendationItem(BaseModel):
    internship: InternshipResponse
    score_breakdown: FitScoreBreakdown

class RecommendationsResponse(BaseModel):
    student_id: int
    count: int
    recommendations: List[RecommendationItem]

# --- Skill Gap ---
class SkillGapRequest(BaseModel):
    student_id: Optional[int] = 1
    internship_id: int

class SkillGapResponse(BaseModel):
    internship_id: int
    internship_title: str
    company: str
    matched_required_skills: List[str]
    missing_required_skills: List[str]
    matched_preferred_skills: List[str]
    missing_preferred_skills: List[str]
    readiness_level: str  # High, Moderate, Needs Preparation
    explanation: str

# --- Learning Resources & Plan ---
class LearningResourceItem(BaseModel):
    title: str
    url: str
    skill_tag: str
    resource_type: str
    description: Optional[str]
    is_verified: bool

class LearningPlanStep(BaseModel):
    week_number: int
    skill: str
    action_item: str
    practice_project: str
    resources: List[LearningResourceItem] = []

class LearningPlanRequest(BaseModel):
    missing_skills: List[str]
    target_role: Optional[str] = "Software Engineer"
    time_budget_weeks: Optional[int] = 4

class LearningPlanResponse(BaseModel):
    target_role: str
    total_weeks: int
    skills_addressed: List[str]
    steps: List[LearningPlanStep]
    summary_guidance: str

# --- ReAct Agent Chat ---
class AgentChatRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    student_id: Optional[int] = 1

class AgentToolCallLog(BaseModel):
    tool_name: str
    tool_args: Dict[str, Any]
    observation_summary: str
    duration_ms: Optional[float] = 0.0

class AgentChatResponse(BaseModel):
    response: str
    tool_logs: List[AgentToolCallLog] = []
    grounded_evidence: Dict[str, Any] = {}
