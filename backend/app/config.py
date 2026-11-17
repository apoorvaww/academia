import os
from pathlib import Path

# Ensure SQLAlchemy pure Python collections are used under restrictive OS environments
os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/academia.db")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# Maximum size for PDF upload: 5 MB
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt"}

# Security limits for ReAct agent
AGENT_MAX_ITERATIONS = 5
AGENT_MAX_QUERY_LENGTH = 1000
