import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DATABASE_URL
from app.models.database import engine, Base, SessionLocal
from app.models.entities import Student, Internship, LearningResource, Skill, StudentSkill
from app.data.seed_data import SAMPLE_INTERNSHIPS, TRUSTED_LEARNING_RESOURCES
from app.services.skill_extractor import normalize_skill
from app.services.recommender import build_faiss_index

from app.api.health import router as health_router
from app.api.profile import router as profile_router
from app.api.internships import router as internships_router
from app.api.agent import router as agent_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("academia_portal")

def seed_database():
    """Initializes tables and seeds curated internships and learning resources if empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        internship_count = db.query(Internship).count()
        if internship_count == 0:
            logger.info("Seeding curated sample internships...")
            for item in SAMPLE_INTERNSHIPS:
                internship = Internship(
                    id=item["id"],
                    title=item["title"],
                    company=item["company"],
                    location=item["location"],
                    work_mode=item["work_mode"],
                    description=item["description"],
                    required_skills=json.dumps(item["required_skills"]),
                    preferred_skills=json.dumps(item["preferred_skills"]),
                    status=item["status"],
                    source_label=item["source_label"]
                )
                db.add(internship)
            db.commit()

        resource_count = db.query(LearningResource).count()
        if resource_count == 0:
            logger.info("Seeding trusted learning resources...")
            for res in TRUSTED_LEARNING_RESOURCES:
                lr = LearningResource(
                    title=res["title"],
                    url=res["url"],
                    skill_tag=normalize_skill(res["skill_tag"]),
                    resource_type=res["resource_type"],
                    description=res["description"],
                    is_verified=True
                )
                db.add(lr)
            db.commit()

        # Build or refresh the in-memory FAISS index
        active_internships = db.query(Internship).filter(Internship.status == "open").all()
        build_faiss_index(active_internships)
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Academia-Industry Portal Backend...")
    seed_database()
    yield
    # Shutdown
    logger.info("Shutting down backend...")

app = FastAPI(
    title="Academia–Industry Collaboration Portal API",
    description="Skill Mapping, Internship Recommendations, and ReAct Career Copilot Agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(profile_router)
app.include_router(internships_router)
app.include_router(agent_router)

@app.get("/")
def root():
    return {
        "message": "Academia–Industry Collaboration Portal API is running.",
        "documentation": "/docs",
        "health": "/health"
    }
