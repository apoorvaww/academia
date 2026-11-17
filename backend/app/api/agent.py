import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import AgentChatRequest, AgentChatResponse
from app.agent.react_agent import run_agent_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["AI Career Agent"])

@router.post("/chat", response_model=AgentChatResponse)
def chat_with_career_agent(req: AgentChatRequest, db: Session = Depends(get_db)):
    """
    Executes a bounded, tool-using ReAct AI career copilot request.
    Uses real database tools (search_internships, analyze_skill_gap, create_learning_plan),
    enforces server-side authorization, and returns grounded answers with tool traces.
    """
    student_id = req.student_id or 1
    try:
        return run_agent_chat(db, student_id, req.query)
    except Exception as e:
        logger.error(f"Error in agent chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent service encountered an error: {str(e)}")
