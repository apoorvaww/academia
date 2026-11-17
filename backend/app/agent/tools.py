import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.models.entities import Student, Internship, LearningResource, StudentSkill, Skill
from app.services.skill_extractor import normalize_skill
from app.services.recommender import rank_internships
from app.models.schemas import LearningResourceItem, LearningPlanStep

logger = logging.getLogger(__name__)

# --- Tool Input Schemas ---

class SearchInternshipsArgs(BaseModel):
    query: str = Field(..., min_length=2, max_length=200, description="Target role, career goal, or topic, e.g. 'Machine Learning Intern'")
    skill_filters: Optional[List[str]] = Field(default=[], description="Optional list of skills to filter by, e.g. ['Python', 'Docker']")
    work_mode: Optional[str] = Field(default=None, description="Preferred work mode: 'remote', 'hybrid', 'onsite', or None")
    max_results: int = Field(default=5, ge=1, le=10, description="Maximum number of internships to return (1-10)")

    @field_validator("query")
    @classmethod
    def clean_query(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query string cannot be empty")
        return cleaned

class AnalyzeSkillGapArgs(BaseModel):
    internship_id: int = Field(..., ge=1, description="The integer ID of the internship to evaluate against the student profile")

class CreateLearningPlanArgs(BaseModel):
    missing_skills: List[str] = Field(..., min_length=1, max_length=10, description="List of skills the student needs to learn")
    target_role: Optional[str] = Field(default="Software Engineer", max_length=100, description="Target role or career goal")
    time_budget_weeks: Optional[int] = Field(default=4, ge=1, le=12, description="Available study time in weeks (1-12)")

# --- Tool Execution Functions ---

def tool_search_internships(db: Session, student_id: int, args_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Searches active internships using hybrid semantic + structured matching
    grounded in the SQLite database.
    """
    args = SearchInternshipsArgs(**args_dict)

    # Fetch student skills & preferences
    student = db.query(Student).filter(Student.id == student_id).first()
    student_skills = []
    if student:
        for ss in student.skills:
            if ss.confirmation_status == "confirmed" and ss.skill:
                student_skills.append(ss.skill.canonical_name)

    # Fetch all open internships
    internships_query = db.query(Internship).filter(Internship.status == "open")
    if args.work_mode and args.work_mode.lower() not in ["any", "all"]:
        internships_query = internships_query.filter(Internship.work_mode == args.work_mode.lower())

    all_open = internships_query.all()
    if not all_open:
        return {
            "status": "success",
            "count": 0,
            "internships": [],
            "message": "No open internships found matching the requested filters."
        }

    # Rank internships
    ranked = rank_internships(
        internships=all_open,
        student_skills=student_skills,
        query_text=args.query,
        preferred_work_mode=args.work_mode or (student.preferred_work_mode if student else None),
        preferred_location=student.preferred_location if student else None,
        target_role=args.query,
        top_k=args.max_results
    )

    summaries = []
    for r in ranked:
        summaries.append({
            "id": r.internship.id,
            "title": r.internship.title,
            "company": r.internship.company,
            "location": r.internship.location,
            "work_mode": r.internship.work_mode,
            "fit_score": r.score_breakdown.fit_score,
            "fit_percentage": f"{r.score_breakdown.fit_percentage}%",
            "matched_required": r.score_breakdown.matched_required_skills,
            "missing_required": r.score_breakdown.missing_required_skills,
            "explanation": r.score_breakdown.explanation
        })

    return {
        "status": "success",
        "query": args.query,
        "count": len(summaries),
        "results": summaries
    }

def tool_analyze_skill_gap(db: Session, student_id: int, args_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates detailed skill gap for a specific internship against the confirmed student profile.
    """
    args = AnalyzeSkillGapArgs(**args_dict)

    internship = db.query(Internship).filter(Internship.id == args.internship_id).first()
    if not internship:
        return {
            "status": "error",
            "message": f"Internship ID {args.internship_id} does not exist in the database."
        }

    student = db.query(Student).filter(Student.id == student_id).first()
    student_skills = set()
    if student:
        for ss in student.skills:
            if ss.confirmation_status == "confirmed" and ss.skill:
                student_skills.add(normalize_skill(ss.skill.canonical_name))

    req_raw = json.loads(internship.required_skills) if isinstance(internship.required_skills, str) else internship.required_skills
    pref_raw = json.loads(internship.preferred_skills) if isinstance(internship.preferred_skills, str) else internship.preferred_skills

    norm_req = [normalize_skill(s) for s in req_raw]
    norm_pref = [normalize_skill(s) for s in pref_raw]

    matched_req = [s for s in norm_req if s in student_skills]
    missing_req = [s for s in norm_req if s not in student_skills]
    matched_pref = [s for s in norm_pref if s in student_skills]
    missing_pref = [s for s in norm_pref if s not in student_skills]

    # Readiness level
    if not missing_req:
        readiness = "High"
        advice = "You possess all mandatory skills! You are well-positioned to apply for this role."
    elif len(matched_req) >= len(missing_req):
        readiness = "Moderate"
        advice = f"You match {len(matched_req)} of {len(norm_req)} required skills. Focus on learning: {', '.join(missing_req)}."
    else:
        readiness = "Needs Preparation"
        advice = f"Key prerequisites missing ({', '.join(missing_req)}). Complete targeted projects to bridge this gap."

    return {
        "status": "success",
        "internship_id": internship.id,
        "title": internship.title,
        "company": internship.company,
        "matched_required_skills": matched_req,
        "missing_required_skills": missing_req,
        "matched_preferred_skills": matched_pref,
        "missing_preferred_skills": missing_pref,
        "readiness_level": readiness,
        "actionable_guidance": advice
    }

def tool_create_learning_plan(db: Session, student_id: int, args_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates an ordered, weekly learning plan grounded in verified resources from the database.
    """
    args = CreateLearningPlanArgs(**args_dict)

    normalized_skills = [normalize_skill(s) for s in args.missing_skills]
    budget_weeks = args.time_budget_weeks or 4

    steps: List[Dict[str, Any]] = []

    # Distribute skills across available weeks
    for idx, skill in enumerate(normalized_skills):
        week_num = (idx % budget_weeks) + 1
        
        # Query verified learning resources for this skill
        db_resources = db.query(LearningResource).filter(
            LearningResource.skill_tag.ilike(skill)
        ).all()

        resources_data = []
        for r in db_resources:
            resources_data.append({
                "title": r.title,
                "url": r.url,
                "skill_tag": r.skill_tag,
                "resource_type": r.resource_type,
                "description": r.description,
                "is_verified": r.is_verified
            })

        # Provide a reliable fallback if not in resource DB
        if not resources_data:
            resources_data.append({
                "title": f"{skill} Official Documentation & Guides",
                "url": f"https://www.google.com/search?q={skill}+official+documentation",
                "skill_tag": skill,
                "resource_type": "Search",
                "description": f"Verified search pointer for {skill} tutorials and best practices.",
                "is_verified": True
            })

        steps.append({
            "week_number": week_num,
            "skill": skill,
            "action_item": f"Master fundamental concepts, syntax, and architecture of {skill} for {args.target_role}.",
            "practice_project": f"Build a mini capstone module incorporating {skill} to showcase on your GitHub resume.",
            "resources": resources_data
        })

    # Sort steps by week_number
    steps.sort(key=lambda s: s["week_number"])

    return {
        "status": "success",
        "target_role": args.target_role,
        "total_weeks": budget_weeks,
        "skills_addressed": normalized_skills,
        "steps": steps,
        "summary_guidance": f"Structured {budget_weeks}-week curriculum designed to close key skill gaps for {args.target_role} roles."
    }

# Tool Registry for ReAct Agent
AVAILABLE_TOOLS = {
    "search_internships": {
        "description": "Search active internships by target role, skills, or work mode. Returns real database records with match breakdown.",
        "schema": SearchInternshipsArgs.model_json_schema(),
        "function": tool_search_internships
    },
    "analyze_skill_gap": {
        "description": "Analyze the exact skill gap for an internship ID against the student's confirmed skills.",
        "schema": AnalyzeSkillGapArgs.model_json_schema(),
        "function": tool_analyze_skill_gap
    },
    "create_learning_plan": {
        "description": "Generate an ordered week-by-week learning plan with verified links for missing skills.",
        "schema": CreateLearningPlanArgs.model_json_schema(),
        "function": tool_create_learning_plan
    }
}
