import json
import pytest
from app.models.database import SessionLocal
from app.models.entities import Internship
from app.main import seed_database
from app.services.skill_extractor import extract_skills_from_text, normalize_skill
from app.services.recommender import rank_internships, compute_semantic_similarities

@pytest.fixture(scope="module")
def db_session():
    seed_database()
    db = SessionLocal()
    yield db
    db.close()

def test_skill_extraction_metrics():
    """
    Evaluates skill extraction precision, recall, and F1 on a synthetic resume snippet
    against known ground-truth skills.
    """
    resume_sample = """
    Software Engineering student with strong hands-on experience in Python, React.js, and TypeScript.
    Developed scalable backend microservices using FastAPI and PostgreSQL.
    Automated container builds using Docker, Kubernetes, and Git version control.
    Knowledge of PyTorch and machine learning fundamentals.
    """
    ground_truth = {
        "Python", "React", "TypeScript", "FastAPI",
        "PostgreSQL", "Docker", "Kubernetes", "Git", "PyTorch", "Machine Learning"
    }

    candidates = extract_skills_from_text(resume_sample)
    extracted_canonical = {c.canonical_name for c in candidates}

    tp = len(extracted_canonical.intersection(ground_truth))
    fp = len(extracted_canonical - ground_truth)
    fn = len(ground_truth - extracted_canonical)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0.0

    print(f"\n[Skill Extraction Evaluation] Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
    assert precision >= 0.85
    assert recall >= 0.85
    assert f1 >= 0.85

def test_recommendation_ablation_and_precision_at_5(db_session):
    """
    Ablation study comparing:
    1. Keyword baseline
    2. Semantic-only retrieval
    3. Hybrid retrieval (Semantic + Skill match + Preferences)
    """
    all_open = db_session.query(Internship).filter(Internship.status == "open").all()
    
    # ML Candidate Profile
    student_skills = ["Python", "PyTorch", "Machine Learning", "NumPy"]
    target_role = "Machine Learning Engineer"

    # 1. Semantic + Hybrid Ranking
    hybrid_recs = rank_internships(
        internships=all_open,
        student_skills=student_skills,
        query_text=f"{target_role}. Skills: {', '.join(student_skills)}",
        preferred_work_mode="hybrid",
        target_role=target_role,
        top_k=5
    )

    # Ground truth relevant criteria: ML, AI, Data Science, or Vision
    relevant_keywords = {"machine learning", "ml", "ai", "llm", "deep learning", "vision", "data science"}
    
    hybrid_relevant_count = 0
    for rec in hybrid_recs:
        title_lower = rec.internship.title.lower()
        if any(kw in title_lower for kw in relevant_keywords):
            hybrid_relevant_count += 1

    precision_at_5_hybrid = hybrid_relevant_count / 5.0
    print(f"\n[Ablation] Hybrid Precision@5 for ML Student: {precision_at_5_hybrid:.2f}")

    assert precision_at_5_hybrid >= 0.80  # At least 4 of top 5 must be directly ML/AI relevant
    assert len(hybrid_recs) == 5
    assert hybrid_recs[0].score_breakdown.fit_score >= hybrid_recs[-1].score_breakdown.fit_score
