import io
import re
from typing import Tuple, Optional
import pypdf
from app.services.skill_extractor import extract_skills_from_text
from app.models.schemas import ResumeParseResponse, CandidateSkill

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract clean text from a text-based PDF using pypdf."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        extracted_pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
        return "\n".join(extracted_pages).strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF document: {str(e)}")

def parse_resume(content: bytes, filename: str) -> ResumeParseResponse:
    """
    Parses resume content (PDF or plain text), identifies candidate contact info
    and candidate skills with evidence. Does not persist raw bytes or log sensitive data.
    """
    if filename.lower().endswith(".pdf"):
        raw_text = extract_text_from_pdf(content)
    else:
        try:
            raw_text = content.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = content.decode("latin-1", errors="ignore")

    if len(raw_text.strip()) < 15:
        raise ValueError("Could not extract sufficient text from this document. Please ensure it is a text-based PDF or paste your resume text manually.")

    # Basic heuristic extraction for candidate email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)
    detected_email = email_match.group(0) if email_match else None

    # Basic heuristic extraction for candidate name (first line or prominent title)
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    detected_name = None
    if lines:
        first_line = lines[0]
        # Ignore common headings
        if len(first_line.split()) <= 4 and not any(kw in first_line.lower() for kw in ["resume", "curriculum", "cv", "profile"]):
            detected_name = first_line

    candidate_skills = extract_skills_from_text(raw_text)

    # Preview snippet for user review (safe, limited length)
    preview = raw_text[:400] + ("..." if len(raw_text) > 400 else "")

    return ResumeParseResponse(
        detected_name=detected_name,
        detected_email=detected_email,
        candidate_skills=candidate_skills,
        text_preview=preview
    )
