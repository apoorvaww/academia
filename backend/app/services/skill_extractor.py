import re
from typing import List, Dict, Tuple, Optional, Any
from app.models.schemas import CandidateSkill

# Canonical skill taxonomy with comprehensive aliases
SKILL_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Python": {
        "category": "Programming Languages",
        "aliases": ["python", "python3", "py"]
    },
    "JavaScript": {
        "category": "Programming Languages",
        "aliases": ["javascript", "js", "ecmascript", "es6"]
    },
    "TypeScript": {
        "category": "Programming Languages",
        "aliases": ["typescript", "ts"]
    },
    "Java": {
        "category": "Programming Languages",
        "aliases": ["java", "jvm"]
    },
    "C++": {
        "category": "Programming Languages",
        "aliases": ["c++", "cpp"]
    },
    "Go": {
        "category": "Programming Languages",
        "aliases": ["golang", "go programming"]
    },
    "SQL": {
        "category": "Databases",
        "aliases": ["sql", "relational database", "rdbms"]
    },
    "PostgreSQL": {
        "category": "Databases",
        "aliases": ["postgresql", "postgres", "psql"]
    },
    "MongoDB": {
        "category": "Databases",
        "aliases": ["mongodb", "mongo", "nosql"]
    },
    "Redis": {
        "category": "Databases",
        "aliases": ["redis", "in-memory database"]
    },
    "React": {
        "category": "Frontend Frameworks",
        "aliases": ["react", "react.js", "reactjs"]
    },
    "Next.js": {
        "category": "Frontend Frameworks",
        "aliases": ["next.js", "nextjs"]
    },
    "Vue.js": {
        "category": "Frontend Frameworks",
        "aliases": ["vue", "vue.js", "vuejs"]
    },
    "Tailwind CSS": {
        "category": "Frontend Frameworks",
        "aliases": ["tailwind", "tailwindcss"]
    },
    "HTML/CSS": {
        "category": "Frontend Frameworks",
        "aliases": ["html", "html5", "css", "css3"]
    },
    "FastAPI": {
        "category": "Backend Frameworks",
        "aliases": ["fastapi", "fast-api"]
    },
    "Node.js": {
        "category": "Backend Frameworks",
        "aliases": ["node.js", "nodejs", "node"]
    },
    "Django": {
        "category": "Backend Frameworks",
        "aliases": ["django"]
    },
    "Flask": {
        "category": "Backend Frameworks",
        "aliases": ["flask"]
    },
    "REST API": {
        "category": "Backend Architecture",
        "aliases": ["rest api", "restful api", "rest apis", "restful"]
    },
    "GraphQL": {
        "category": "Backend Architecture",
        "aliases": ["graphql"]
    },
    "Docker": {
        "category": "DevOps & Cloud",
        "aliases": ["docker", "containerization", "containers"]
    },
    "Kubernetes": {
        "category": "DevOps & Cloud",
        "aliases": ["kubernetes", "k8s"]
    },
    "AWS": {
        "category": "DevOps & Cloud",
        "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"]
    },
    "CI/CD": {
        "category": "DevOps & Cloud",
        "aliases": ["ci/cd", "cicd", "continuous integration", "github actions", "gitlab ci"]
    },
    "Linux": {
        "category": "Systems & Tools",
        "aliases": ["linux", "unix", "bash", "shell scripting"]
    },
    "Git": {
        "category": "Systems & Tools",
        "aliases": ["git", "github", "gitlab", "version control"]
    },
    "Machine Learning": {
        "category": "AI & Data Science",
        "aliases": ["machine learning", "ml", "statistical learning"]
    },
    "Deep Learning": {
        "category": "AI & Data Science",
        "aliases": ["deep learning", "neural networks", "dl"]
    },
    "PyTorch": {
        "category": "AI & Data Science",
        "aliases": ["pytorch", "torch"]
    },
    "TensorFlow": {
        "category": "AI & Data Science",
        "aliases": ["tensorflow", "tf", "keras"]
    },
    "Scikit-Learn": {
        "category": "AI & Data Science",
        "aliases": ["scikit-learn", "sklearn"]
    },
    "Pandas": {
        "category": "AI & Data Science",
        "aliases": ["pandas"]
    },
    "NumPy": {
        "category": "AI & Data Science",
        "aliases": ["numpy"]
    },
    "NLP": {
        "category": "AI & Data Science",
        "aliases": ["natural language processing", "nlp", "text analytics", "tokenization"]
    },
    "Computer Vision": {
        "category": "AI & Data Science",
        "aliases": ["computer vision", "opencv", "object detection", "image classification"]
    },
    "LLMs": {
        "category": "AI & Data Science",
        "aliases": ["large language models", "llm", "llms", "prompt engineering", "langchain", "llamaindex"]
    },
    "Sentence Transformers": {
        "category": "AI & Data Science",
        "aliases": ["sentence transformers", "sentence-transformers", "sbert", "embeddings"]
    },
    "FAISS": {
        "category": "AI & Data Science",
        "aliases": ["faiss", "vector search", "vector database", "vector index", "chromadb"]
    },
    "Cybersecurity": {
        "category": "Security",
        "aliases": ["cybersecurity", "information security", "infosec", "penetration testing", "owasp"]
    }
}

# Inverted index: lower-case alias -> canonical name
ALIAS_MAP: Dict[str, str] = {}
for canonical, details in SKILL_TAXONOMY.items():
    ALIAS_MAP[canonical.lower()] = canonical
    for alias in details.get("aliases", []):
        ALIAS_MAP[alias.lower()] = canonical

def normalize_skill(name: str) -> str:
    """Normalize any skill string or alias to canonical form."""
    cleaned = name.strip()
    lowered = cleaned.lower()
    return ALIAS_MAP.get(lowered, cleaned.title())

def extract_skills_from_text(text: str) -> List[CandidateSkill]:
    """
    Extract skills from text using boundary-safe regex patterns and return
    matches with surrounding context snippets as evidence.
    """
    if not text:
        return []

    found_skills: Dict[str, CandidateSkill] = {}
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    full_text = " ".join(lines)

    for canonical, details in SKILL_TAXONOMY.items():
        aliases = [canonical] + details.get("aliases", [])
        # Sort aliases by length descending so longer phrases match first
        aliases_sorted = sorted(aliases, key=len, reverse=True)
        
        for alias in aliases_sorted:
            # Safe boundary check
            escaped = re.escape(alias)
            pattern = rf"(?i)(?<!\w){escaped}(?!\w)"
            
            match = re.search(pattern, full_text)
            if match:
                # Find the sentence or line containing the match
                start = max(0, match.start() - 40)
                end = min(len(full_text), match.end() + 40)
                snippet = "..." + full_text[start:end].strip() + "..."
                
                found_skills[canonical] = CandidateSkill(
                    canonical_name=canonical,
                    matched_term=match.group(0),
                    evidence_snippet=snippet,
                    category=details.get("category", "General")
                )
                break  # Don't check other aliases if canonical already found

    return list(found_skills.values())
