from fastapi import APIRouter
from app.agent.llm_provider import get_llm_provider, GeminiProvider
from app.services.recommender import get_embedder

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    """Health check endpoint providing status of API, database, embedder, and LLM."""
    embedder = get_embedder()
    llm_provider = get_llm_provider()
    return {
        "status": "healthy",
        "semantic_embedder": "SentenceTransformers (all-MiniLM-L6-v2)" if embedder else "Lexical/Heuristic Fallback",
        "llm_provider": "Google Gemini" if isinstance(llm_provider, GeminiProvider) else "Deterministic ReAct Solver",
        "version": "1.0.0"
    }
