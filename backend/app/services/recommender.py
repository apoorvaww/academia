import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.services.skill_extractor import normalize_skill
from app.models.schemas import FitScoreBreakdown, RecommendationItem, InternshipResponse
from app.models.entities import Internship

logger = logging.getLogger(__name__)

# Global embedding & FAISS index cache
_EMBEDDER = None
_FAISS_INDEX = None
_INDEX_INTERNSHIP_IDS: List[int] = []

def get_embedder():
    """Lazy load SentenceTransformers embedder with graceful fallback."""
    global _EMBEDDER
    if _EMBEDDER is None:
        try:
            from sentence_transformers import SentenceTransformer
            from app.config import EMBEDDING_MODEL_NAME
            logger.info(f"Loading SentenceTransformer: {EMBEDDING_MODEL_NAME}")
            _EMBEDDER = SentenceTransformer(EMBEDDING_MODEL_NAME)
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Using lexical fallback.")
            _EMBEDDER = False
    return _EMBEDDER

def build_faiss_index(internships: List[Internship]):
    """Build or refresh FAISS index from current active database internships."""
    global _FAISS_INDEX, _INDEX_INTERNSHIP_IDS
    _INDEX_INTERNSHIP_IDS = [item.id for item in internships]

    embedder = get_embedder()
    if not embedder or len(internships) == 0:
        _FAISS_INDEX = None
        return

    try:
        import faiss
        corpus_texts = []
        for item in internships:
            reqs = ", ".join(json.loads(item.required_skills) if isinstance(item.required_skills, str) else item.required_skills)
            prefs = ", ".join(json.loads(item.preferred_skills) if isinstance(item.preferred_skills, str) else item.preferred_skills)
            doc_text = f"{item.title}. {item.description} Required Skills: {reqs}. Preferred Skills: {prefs}."
            corpus_texts.append(doc_text)

        embeddings = embedder.encode(corpus_texts, convert_to_numpy=True, normalize_embeddings=True)
        dimension = embeddings.shape[1]
        
        # Inner Product on normalized vectors is exact Cosine Similarity
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings.astype(np.float32))
        _FAISS_INDEX = index
        logger.info(f"FAISS index built successfully with {len(internships)} internships.")
    except Exception as e:
        logger.error(f"Error building FAISS index: {e}")
        _FAISS_INDEX = None

def compute_semantic_similarities(query_text: str, internships: List[Internship]) -> Dict[int, float]:
    """
    Computes semantic similarity for each internship (0.0 to 1.0) using FAISS
    or lexical fallback if embeddings are unavailable.
    """
    global _FAISS_INDEX, _INDEX_INTERNSHIP_IDS
    results: Dict[int, float] = {}

    if not internships:
        return results

    embedder = get_embedder()

    if embedder and _FAISS_INDEX is not None and len(_INDEX_INTERNSHIP_IDS) == len(internships):
        try:
            query_vec = embedder.encode([query_text], convert_to_numpy=True, normalize_embeddings=True)
            k = len(internships)
            distances, indices = _FAISS_INDEX.search(query_vec.astype(np.float32), k)
            
            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(_INDEX_INTERNSHIP_IDS):
                    internship_id = _INDEX_INTERNSHIP_IDS[idx]
                    # Cosine sim is in [-1, 1], normalize to [0, 1]
                    norm_sim = float(max(0.0, min(1.0, (dist + 1.0) / 2.0)))
                    results[internship_id] = norm_sim
            return results
        except Exception as e:
            logger.warning(f"FAISS search failed ({e}), falling back to token similarity.")

    # Lexical Jaccard / Token Overlap fallback
    query_tokens = set(query_text.lower().replace(",", " ").split())
    for item in internships:
        doc_tokens = set(f"{item.title} {item.description} {item.required_skills}".lower().replace(",", " ").split())
        if not doc_tokens or not query_tokens:
            results[item.id] = 0.3
            continue
        intersection = query_tokens.intersection(doc_tokens)
        union = query_tokens.union(doc_tokens)
        sim = len(intersection) / len(union) if union else 0.0
        # Scale to a reasonable baseline
        results[item.id] = float(min(1.0, sim * 2.5 + 0.2))

    return results

def calculate_fit_breakdown(
    internship: Internship,
    student_skills: List[str],
    semantic_score: float,
    preferred_work_mode: Optional[str] = None,
    preferred_location: Optional[str] = None,
    target_role: Optional[str] = None
) -> FitScoreBreakdown:
    """
    Computes explainable fit score according to formula:
    Fit score = 0.60 * semantic_relevance + 0.30 * skill_match + 0.10 * preference_match
    """
    normalized_student_skills = {normalize_skill(s) for s in student_skills}

    # Parse required and preferred skills
    req_skills_raw = json.loads(internship.required_skills) if isinstance(internship.required_skills, str) else internship.required_skills
    pref_skills_raw = json.loads(internship.preferred_skills) if isinstance(internship.preferred_skills, str) else internship.preferred_skills

    normalized_req = [normalize_skill(s) for s in req_skills_raw]
    normalized_pref = [normalize_skill(s) for s in pref_skills_raw]

    matched_req = [s for s in normalized_req if s in normalized_student_skills]
    missing_req = [s for s in normalized_req if s not in normalized_student_skills]
    matched_pref = [s for s in normalized_pref if s in normalized_student_skills]

    # Weighted Skill Match: weight 1.0 for required, 0.5 for preferred
    total_req_weight = len(normalized_req) * 1.0
    total_pref_weight = len(normalized_pref) * 0.5
    total_weight = total_req_weight + total_pref_weight

    if total_weight > 0:
        matched_weight = (len(matched_req) * 1.0) + (len(matched_pref) * 0.5)
        skill_score = min(1.0, max(0.0, matched_weight / total_weight))
    else:
        skill_score = 0.5  # Neutral default if no skills specified

    # Preference Match (Work mode + Location + Role)
    pref_matches = 0
    pref_criteria_count = 0

    if preferred_work_mode and preferred_work_mode.lower() not in ["any", ""]:
        pref_criteria_count += 1
        if internship.work_mode.lower() == preferred_work_mode.lower() or preferred_work_mode.lower() == "any":
            pref_matches += 1

    if preferred_location and preferred_location.lower() not in ["any", ""]:
        pref_criteria_count += 1
        if internship.work_mode.lower() == "remote" or preferred_location.lower() in internship.location.lower():
            pref_matches += 1

    if target_role and target_role.strip():
        pref_criteria_count += 1
        role_tokens = set(target_role.lower().split())
        title_tokens = set(internship.title.lower().split())
        if role_tokens.intersection(title_tokens):
            pref_matches += 1

    if pref_criteria_count > 0:
        preference_score = pref_matches / pref_criteria_count
    else:
        # Student did not provide preferences; do not penalize
        preference_score = 1.0

    # Combined formula
    semantic_clamped = max(0.0, min(1.0, semantic_score))
    fit_score = (0.60 * semantic_clamped) + (0.30 * skill_score) + (0.10 * preference_score)
    fit_percentage = int(round(fit_score * 100))

    # Construct explainable feedback summary
    explanation_parts = []
    if matched_req:
        explanation_parts.append(f"Strong match on required skills: {', '.join(matched_req)}")
    if missing_req:
        explanation_parts.append(f"Missing {len(missing_req)} required skill(s): {', '.join(missing_req)}")
    else:
        explanation_parts.append("All required skills satisfied!")
    if matched_pref:
        explanation_parts.append(f"Bonus match on preferred: {', '.join(matched_pref)}")
    if preference_score >= 0.8:
        explanation_parts.append("Aligns with work mode and career goals.")

    explanation = ". ".join(explanation_parts) + "."

    return FitScoreBreakdown(
        semantic_score=round(semantic_clamped, 3),
        skill_score=round(skill_score, 3),
        preference_score=round(preference_score, 3),
        fit_score=round(fit_score, 3),
        fit_percentage=fit_percentage,
        matched_required_skills=matched_req,
        missing_required_skills=missing_req,
        matched_preferred_skills=matched_pref,
        explanation=explanation
    )

def rank_internships(
    internships: List[Internship],
    student_skills: List[str],
    query_text: str,
    preferred_work_mode: Optional[str] = None,
    preferred_location: Optional[str] = None,
    target_role: Optional[str] = None,
    top_k: int = 10
) -> List[RecommendationItem]:
    """
    Ranks given internships using hybrid semantic + structured matching.
    """
    if not internships:
        return []

    # 1. Compute semantic similarities
    semantic_map = compute_semantic_similarities(query_text, internships)

    # 2. Score and construct recommendation items
    items: List[RecommendationItem] = []
    for item in internships:
        # Exclude closed internships
        if item.status != "open":
            continue

        sem_score = semantic_map.get(item.id, 0.4)
        breakdown = calculate_fit_breakdown(
            internship=item,
            student_skills=student_skills,
            semantic_score=sem_score,
            preferred_work_mode=preferred_work_mode,
            preferred_location=preferred_location,
            target_role=target_role
        )

        req_list = json.loads(item.required_skills) if isinstance(item.required_skills, str) else item.required_skills
        pref_list = json.loads(item.preferred_skills) if isinstance(item.preferred_skills, str) else item.preferred_skills

        dto = InternshipResponse(
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

        items.append(RecommendationItem(internship=dto, score_breakdown=breakdown))

    # 3. Sort by fit_score descending
    items.sort(key=lambda x: x.score_breakdown.fit_score, reverse=True)
    return items[:top_k]
