import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import Student, Skill, StudentSkill
from app.models.schemas import (
    StudentProfileCreate,
    StudentProfileUpdate,
    StudentProfileResponse,
    ResumeParseResponse,
    SkillConfirmationRequest,
    SkillEvidenceItem
)
from app.services.skill_extractor import normalize_skill, extract_skills_from_text
from app.services.resume_parser import parse_resume
from app.config import MAX_UPLOAD_SIZE_BYTES, ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["Profile & Resume"])

def get_or_create_skill(db: Session, canonical_name: str) -> Skill:
    norm_name = normalize_skill(canonical_name)
    skill = db.query(Skill).filter(Skill.canonical_name.ilike(norm_name)).first()
    if not skill:
        skill = Skill(canonical_name=norm_name, category="Technical")
        db.add(skill)
        db.commit()
        db.refresh(skill)
    return skill

@router.get("", response_model=StudentProfileResponse)
def get_current_profile(student_id: int = 1, db: Session = Depends(get_db)):
    """Retrieve the student's current profile with confirmed skills."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        # Create a default student profile for instant evaluation and demo
        student = Student(
            id=1,
            name="Aarav Sharma",
            email="aarav.sharma@university.edu",
            degree="B.Tech Computer Science",
            major="Artificial Intelligence & Data Engineering",
            graduation_year=2026,
            target_role="Machine Learning Engineer",
            preferred_location="Any",
            preferred_work_mode="remote",
            bio="Third-year CS undergraduate interested in agentic AI, NLP, and scalable backend systems."
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # Add initial confirmed skills
        initial_skills = [
            ("Python", "Coursework & Projects", "advanced"),
            ("Machine Learning", "Academic Thesis Project", "intermediate"),
            ("NumPy", "Coursework & Labs", "intermediate"),
            ("Git", "Open Source Projects", "intermediate")
        ]
        for name, src, prof in initial_skills:
            sk = get_or_create_skill(db, name)
            ss = StudentSkill(
                student_id=student.id,
                skill_id=sk.id,
                evidence_source=src,
                confirmation_status="confirmed",
                proficiency=prof
            )
            db.add(ss)
        db.commit()
        db.refresh(student)

    # Format skills for response
    skills_dto = []
    for ss in student.skills:
        if ss.skill:
            skills_dto.append(SkillEvidenceItem(
                canonical_name=ss.skill.canonical_name,
                evidence_source=ss.evidence_source,
                proficiency=ss.proficiency,
                confirmation_status=ss.confirmation_status
            ))

    return StudentProfileResponse(
        id=student.id,
        name=student.name,
        email=student.email,
        degree=student.degree,
        major=student.major,
        graduation_year=student.graduation_year,
        target_role=student.target_role,
        preferred_location=student.preferred_location,
        preferred_work_mode=student.preferred_work_mode,
        bio=student.bio,
        skills=skills_dto
    )

@router.put("", response_model=StudentProfileResponse)
@router.post("", response_model=StudentProfileResponse)
def update_profile(profile_data: StudentProfileUpdate, student_id: int = 1, db: Session = Depends(get_db)):
    """Update student profile background details and target preferences."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    if profile_data.name is not None:
        student.name = profile_data.name.strip()
    if profile_data.email is not None:
        student.email = profile_data.email
    if profile_data.degree is not None:
        student.degree = profile_data.degree.strip()
    if profile_data.major is not None:
        student.major = profile_data.major.strip()
    if profile_data.graduation_year is not None:
        student.graduation_year = profile_data.graduation_year
    if profile_data.target_role is not None:
        student.target_role = profile_data.target_role.strip()
    if profile_data.preferred_location is not None:
        student.preferred_location = profile_data.preferred_location.strip()
    if profile_data.preferred_work_mode is not None:
        student.preferred_work_mode = profile_data.preferred_work_mode.strip()
    if profile_data.bio is not None:
        student.bio = profile_data.bio.strip()

    db.commit()
    db.refresh(student)
    return get_current_profile(student_id=student.id, db=db)

@router.post("/resume/parse", response_model=ResumeParseResponse)
async def upload_and_parse_resume(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    """
    Parses resume text from an uploaded PDF or submitted text.
    Extracts candidate skills with evidence snippets for student confirmation.
    """
    if file:
        ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Only text-based PDF or plain text files are allowed."
            )

        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB."
            )

        try:
            return parse_resume(content, file.filename)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    elif raw_text and len(raw_text.strip()) > 10:
        candidate_skills = extract_skills_from_text(raw_text)
        preview = raw_text[:300] + "..." if len(raw_text) > 300 else raw_text
        return ResumeParseResponse(
            detected_name=None,
            detected_email=None,
            candidate_skills=candidate_skills,
            text_preview=preview
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid PDF resume file or paste resume text."
        )

@router.post("/skills/confirm", response_model=StudentProfileResponse)
def confirm_skills(request: SkillConfirmationRequest, student_id: int = 1, db: Session = Depends(get_db)):
    """
    Saves confirmed skills to the student profile after student review.
    Replaces existing confirmed skills with the validated set.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    # Remove existing associations
    db.query(StudentSkill).filter(StudentSkill.student_id == student_id).delete()

    for item in request.skills:
        skill_entity = get_or_create_skill(db, item.canonical_name)
        student_skill = StudentSkill(
            student_id=student_id,
            skill_id=skill_entity.id,
            evidence_source=item.evidence_source or "User Confirmed",
            confirmation_status="confirmed",
            proficiency=item.proficiency or "intermediate"
        )
        db.add(student_skill)

    db.commit()
    db.refresh(student)
    return get_current_profile(student_id=student_id, db=db)
