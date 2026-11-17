import pytest
from app.models.database import SessionLocal, Base, engine
from app.main import seed_database
from app.agent.tools import (
    tool_search_internships,
    tool_analyze_skill_gap,
    tool_create_learning_plan,
    SearchInternshipsArgs,
    AnalyzeSkillGapArgs,
    CreateLearningPlanArgs
)

@pytest.fixture(scope="module")
def db_session():
    seed_database()
    db = SessionLocal()
    yield db
    db.close()

def test_tool_search_internships(db_session):
    args = {"query": "Machine Learning", "max_results": 3}
    result = tool_search_internships(db_session, student_id=1, args_dict=args)
    assert result["status"] == "success"
    assert result["count"] > 0
    assert len(result["results"]) <= 3
    # Check returned keys
    first = result["results"][0]
    assert "id" in first
    assert "title" in first
    assert "fit_percentage" in first

def test_tool_analyze_skill_gap(db_session):
    # Test with internship #1 (ML Engineer)
    args = {"internship_id": 1}
    result = tool_analyze_skill_gap(db_session, student_id=1, args_dict=args)
    assert result["status"] == "success"
    assert "matched_required_skills" in result
    assert "missing_required_skills" in result
    assert "readiness_level" in result

def test_tool_create_learning_plan(db_session):
    args = {
        "missing_skills": ["PyTorch", "Docker"],
        "target_role": "Machine Learning Engineer",
        "time_budget_weeks": 4
    }
    result = tool_create_learning_plan(db_session, student_id=1, args_dict=args)
    assert result["status"] == "success"
    assert result["total_weeks"] == 4
    assert len(result["steps"]) == 2
    # Check verified resource
    first_step = result["steps"][0]
    assert len(first_step["resources"]) > 0
    assert first_step["resources"][0]["url"].startswith("http")

def test_tool_invalid_args_rejection():
    with pytest.raises(Exception):
        SearchInternshipsArgs(query="", max_results=50) # Invalid query and bounds
    with pytest.raises(Exception):
        AnalyzeSkillGapArgs(internship_id=-1)
    with pytest.raises(Exception):
        CreateLearningPlanArgs(missing_skills=[], time_budget_weeks=20)
