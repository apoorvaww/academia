import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import Student, Internship
from app.models.schemas import (
    RecommendationsResponse,
    RecommendationItem,
    InternshipResponse,
    SkillGapRequest,
    SkillGapResponse,
    LearningPlanRequest,
    LearningPlanResponse
)
from app.services.recommender import rank_internships, calculate_fit_breakdown, compute_semantic_similarities
from app.agent.tools import tool_analyze_skill_gap, tool_create_learning_plan

router = APIRouter(tags=["Internships & Recommendations"])

@router.get("/internships/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    student_id: int = 1,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Returns explainable internship recommendations ranked by the hybrid formula:
    Fit score = 0.60 * semantic_relevance + 0.30 * skill_match + 0.10 * preference_match
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    student_skills = []
    for ss in student.skills:
        if ss.confirmation_status == "confirmed" and ss.skill:
            student_skills.append(ss.skill.canonical_name)

    all_open = db.query(Internship).filter(Internship.status == "open").all()
    if not all_open:
        return RecommendationsResponse(student_id=student_id, count=0, recommendations=[])

    query_text = f"{student.target_role or 'Software Engineer'}. Skills: {', '.join(student_skills)}."
    
    ranked = rank_internships(
        internships=all_open,
        student_skills=student_skills,
        query_text=query_text,
        preferred_work_mode=student.preferred_work_mode,
        preferred_location=student.preferred_location,
        target_role=student.target_role,
        top_k=limit
    )

    return RecommendationsResponse(
        student_id=student_id,
        count=len(ranked),
        recommendations=ranked
    )

@router.get("/internships/{internship_id}", response_model=InternshipResponse)
def get_internship_detail(internship_id: int, db: Session = Depends(get_db)):
    """Fetch details and skill requirements for a single internship record."""
    item = db.query(Internship).filter(Internship.id == internship_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found.")

    req_list = json.loads(item.required_skills) if isinstance(item.required_skills, str) else item.required_skills
    pref_list = json.loads(item.preferred_skills) if isinstance(item.preferred_skills, str) else item.preferred_skills

    return InternshipResponse(
        id=item.id,
        title=item.title,
        company=item.company,
        location=item.location,
        work_mode=item.work_mode,
        description=item.description,
        required_skills=req_list,
        preferred_skills=pref_list,
        status=item.status,
        source_label=item.source_label
    )

@router.post("/skill-gap", response_model=SkillGapResponse)
def analyze_skill_gap_endpoint(req: SkillGapRequest, db: Session = Depends(get_db)):
    """Calculate skill gap analysis between confirmed student skills and an internship."""
    result = tool_analyze_skill_gap(db, req.student_id or 1, {"internship_id": req.internship_id})
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))

    return SkillGapResponse(
        internship_id=result["internship_id"],
        internship_title=result["title"],
        company=result["company"],
        matched_required_skills=result["matched_required_skills"],
        missing_required_skills=result["missing_required_skills"],
        matched_preferred_skills=result["matched_preferred_skills"],
        missing_preferred_skills=result["missing_preferred_skills"],
        readiness_level=result["readiness_level"],
        explanation=result["actionable_guidance"]
    )

@router.post("/learning-plan", response_model=LearningPlanResponse)
def create_learning_plan_endpoint(req: LearningPlanRequest, db: Session = Depends(get_db)):
    """Builds a structured learning plan with verified resources for missing skills."""
    result = tool_create_learning_plan(db, 1, req.model_dump())
    return LearningPlanResponse(
        target_role=result["target_role"],
        total_weeks=result["total_weeks"],
        skills_addressed=result["skills_addressed"],
        steps=result["steps"],
        summary_guidance=result["summary_guidance"]
    )
