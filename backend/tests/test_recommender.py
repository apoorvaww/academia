import json
import pytest
from app.services.skill_extractor import normalize_skill, extract_skills_from_text
from app.services.recommender import calculate_fit_breakdown, rank_internships
from app.models.entities import Internship

def test_skill_normalization():
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("react.js") == "React"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("python3") == "Python"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("sklearn") == "Scikit-Learn"

def test_extract_skills_from_text():
    sample_text = """
    Experienced in Python and React development. Built REST APIs using FastAPI and deployed
    containerized workloads using Docker and Kubernetes. Familiar with PostgreSQL and Git.
    """
    candidates = extract_skills_from_text(sample_text)
    names = {c.canonical_name for c in candidates}
    assert "Python" in names
    assert "React" in names
    assert "FastAPI" in names
    assert "Docker" in names
    assert "Kubernetes" in names
    assert "PostgreSQL" in names
    assert "Git" in names

def test_fit_score_calculation():
    internship = Internship(
        id=99,
        title="ML Engineer Intern",
        company="Test Corp",
        location="Remote",
        work_mode="remote",
        description="Build PyTorch models",
        required_skills=json.dumps(["Python", "PyTorch", "NumPy"]),
        preferred_skills=json.dumps(["Docker"]),
        status="open",
        source_label="[SAMPLE DATA]"
    )

    # Student with 2 required + 1 preferred
    student_skills = ["Python", "PyTorch", "Docker"]
    breakdown = calculate_fit_breakdown(
        internship=internship,
        student_skills=student_skills,
        semantic_score=0.8,
        preferred_work_mode="remote",
        preferred_location="Any",
        target_role="ML Engineer"
    )

    # Required weight: 3 * 1.0 = 3.0. Pref weight: 1 * 0.5 = 0.5. Total = 3.5
    # Matched weight: 2.0 (Python, PyTorch) + 0.5 (Docker) = 2.5
    # Skill score = 2.5 / 3.5 = 0.714
    # Preference score = 1.0 (remote matches, role matches)
    # Fit score = 0.60 * 0.8 + 0.30 * 0.714 + 0.10 * 1.0 = 0.48 + 0.214 + 0.1 = 0.794
    assert breakdown.fit_score > 0.7
    assert breakdown.fit_percentage >= 75
    assert "Python" in breakdown.matched_required_skills
    assert "PyTorch" in breakdown.matched_required_skills
    assert "NumPy" in breakdown.missing_required_skills
    assert "Docker" in breakdown.matched_preferred_skills
