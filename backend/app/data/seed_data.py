import json
from typing import List, Dict, Any

SAMPLE_INTERNSHIPS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Machine Learning Engineer Intern",
        "company": "DeepCognition Labs",
        "location": "Bengaluru",
        "work_mode": "hybrid",
        "description": "Work with our applied AI group building semantic search and recommendation systems. You will train PyTorch models, optimize embeddings, and deploy microservices.",
        "required_skills": ["Python", "Machine Learning", "PyTorch", "NumPy"],
        "preferred_skills": ["Sentence Transformers", "FAISS", "Docker", "FastAPI"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 2,
        "title": "AI & LLM Research Intern",
        "company": "Nexus AI Systems",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Help design and evaluate agentic LLM workflows and retrieval-augmented generation (RAG) pipelines for academic and legal literature analysis.",
        "required_skills": ["Python", "LLMs", "NLP"],
        "preferred_skills": ["FAISS", "Sentence Transformers", "PyTorch", "Git"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 3,
        "title": "Frontend Developer Intern (React + TypeScript)",
        "company": "PixelCraft Technologies",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Collaborate with UI designers to build modern, responsive web portals using React, TypeScript, and Tailwind CSS. Focus on state management and performance.",
        "required_skills": ["React", "TypeScript", "JavaScript", "HTML/CSS"],
        "preferred_skills": ["Tailwind CSS", "Next.js", "Git", "REST API"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 4,
        "title": "Full-Stack Software Engineering Intern",
        "company": "EduBridge Innovation",
        "location": "Hyderabad",
        "work_mode": "hybrid",
        "description": "Develop full-stack web features connecting university placement cells with verified enterprise hiring managers. Work on REST APIs, relational databases, and dynamic interfaces.",
        "required_skills": ["Python", "FastAPI", "React", "SQL"],
        "preferred_skills": ["PostgreSQL", "Docker", "TypeScript", "Git"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 5,
        "title": "Backend API Developer Intern",
        "company": "CloudStream Systems",
        "location": "Pune",
        "work_mode": "onsite",
        "description": "Build high-throughput RESTful services using FastAPI and PostgreSQL. Implement schema validation, caching with Redis, and automated integration testing.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST API"],
        "preferred_skills": ["Redis", "Docker", "Linux", "CI/CD"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 6,
        "title": "Cloud & DevOps Engineering Intern",
        "company": "Aether Infrastructure",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Automate containerized deployment pipelines using Docker, Kubernetes, and GitHub Actions. Monitor cloud services on AWS and improve infrastructure reliability.",
        "required_skills": ["Docker", "Linux", "Git", "CI/CD"],
        "preferred_skills": ["Kubernetes", "AWS", "Python", "SQL"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 7,
        "title": "Data Science & Analytics Intern",
        "company": "QuantPulse Analytics",
        "location": "Mumbai",
        "work_mode": "hybrid",
        "description": "Analyze large student enrollment and industry hiring datasets. Build predictive models, extract statistical insights, and create executive data dashboards.",
        "required_skills": ["Python", "Pandas", "NumPy", "SQL"],
        "preferred_skills": ["Scikit-Learn", "Machine Learning", "Git"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 8,
        "title": "Computer Vision Intern",
        "company": "VividVision AI",
        "location": "Bengaluru",
        "work_mode": "onsite",
        "description": "Work on real-time object detection and video processing models using OpenCV and PyTorch. Benchmark models for edge inference.",
        "required_skills": ["Python", "Computer Vision", "PyTorch", "NumPy"],
        "preferred_skills": ["Deep Learning", "Docker", "C++", "Linux"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 9,
        "title": "Cybersecurity & Security Operations Intern",
        "company": "ShieldPoint Cyber",
        "location": "Delhi NCR",
        "work_mode": "hybrid",
        "description": "Assist our security operations team with vulnerability scanning, penetration testing on web endpoints, and verifying OWASP security hygiene across portal APIs.",
        "required_skills": ["Cybersecurity", "Linux", "REST API"],
        "preferred_skills": ["Python", "Docker", "Git"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 10,
        "title": "NLP & Conversational AI Intern",
        "company": "VerbaTech Solutions",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Build intelligent chatbots and intent classification systems using Hugging Face transformers, fine-tuning, and modern vector databases.",
        "required_skills": ["Python", "NLP", "Machine Learning"],
        "preferred_skills": ["PyTorch", "LLMs", "FAISS", "Sentence Transformers"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 11,
        "title": "Data Engineering Intern (Pipelines & SQL)",
        "company": "DataFlow Networks",
        "location": "Bengaluru",
        "work_mode": "hybrid",
        "description": "Construct automated ETL pipelines, orchestrate data extraction workflows, and write optimized SQL queries for high-volume analytics databases.",
        "required_skills": ["Python", "SQL", "PostgreSQL", "Pandas"],
        "preferred_skills": ["Docker", "Linux", "Git", "CI/CD"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 12,
        "title": "Node.js & Backend Systems Intern",
        "company": "HyperLink Tech",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Develop asynchronous microservices and GraphQL/REST endpoints using Node.js, TypeScript, and MongoDB. Write rigorous unit tests.",
        "required_skills": ["Node.js", "TypeScript", "JavaScript", "REST API"],
        "preferred_skills": ["MongoDB", "Docker", "GraphQL", "Git"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 13,
        "title": "Mobile App Developer Intern (React Native)",
        "company": "OmniApp Studio",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Build intuitive cross-platform mobile experiences for campus recruitment using React Native and TypeScript, consuming backend RESTful APIs.",
        "required_skills": ["React", "JavaScript", "TypeScript", "REST API"],
        "preferred_skills": ["Git", "HTML/CSS", "Node.js"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 14,
        "title": "Applied Generative AI Intern",
        "company": "Synthetix AI",
        "location": "Bengaluru",
        "work_mode": "hybrid",
        "description": "Implement automated document summarization, semantic tagging, and prompt evaluation for enterprise customer knowledge bases.",
        "required_skills": ["Python", "LLMs", "NLP", "Git"],
        "preferred_skills": ["Sentence Transformers", "FastAPI", "Docker"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 15,
        "title": "System Performance & Linux Engineering Intern",
        "company": "KernelLogic Systems",
        "location": "Chennai",
        "work_mode": "onsite",
        "description": "Benchmark low-latency network protocols, write C++ & Python test suites, and configure Linux environments for distributed storage clusters.",
        "required_skills": ["Linux", "C++", "Python", "Git"],
        "preferred_skills": ["Docker", "CI/CD"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 16,
        "title": "Junior Python Web Developer Intern",
        "company": "Ascend Digital",
        "location": "Chandigarh",
        "work_mode": "hybrid",
        "description": "Build internal administrative portals using Django and PostgreSQL. Implement role-based access control and exportable report generators.",
        "required_skills": ["Python", "Django", "SQL", "HTML/CSS"],
        "preferred_skills": ["PostgreSQL", "JavaScript", "Git"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 17,
        "title": "Vector Database & Search Intern",
        "company": "VectorMesh",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Develop high-scale nearest-neighbor search algorithms using FAISS and Sentence Transformers for multi-million item product catalogs.",
        "required_skills": ["Python", "FAISS", "Sentence Transformers", "NumPy"],
        "preferred_skills": ["PyTorch", "Docker", "FastAPI", "C++"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 18,
        "title": "Vue.js Frontend Engineer Intern",
        "company": "BrightSpark Software",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Craft interactive student dashboards, analytics charts, and responsive forms using Vue.js, Tailwind CSS, and REST API integration.",
        "required_skills": ["Vue.js", "JavaScript", "HTML/CSS"],
        "preferred_skills": ["Tailwind CSS", "TypeScript", "Git"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 19,
        "title": "Deep Learning Computer Vision Research Intern",
        "company": "Cognitive Edge",
        "location": "Hyderabad",
        "work_mode": "hybrid",
        "description": "Train and evaluate deep convolutional and transformer vision backbones for autonomous inspection systems using PyTorch and Linux workstations.",
        "required_skills": ["Python", "PyTorch", "Deep Learning", "Computer Vision"],
        "preferred_skills": ["Linux", "Docker", "Git"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    },
    {
        "id": 20,
        "title": "Platform Reliability & Security Intern",
        "company": "SecureNet Ops",
        "location": "Remote",
        "work_mode": "remote",
        "description": "Audit container configurations, implement CI/CD security scanning, and enforce least-privilege policies across cloud deployments.",
        "required_skills": ["Linux", "Docker", "Cybersecurity", "Git"],
        "preferred_skills": ["Kubernetes", "AWS", "CI/CD", "Python"],
        "status": "open",
        "source_label": "[SAMPLE DATA]"
    }
]

TRUSTED_LEARNING_RESOURCES: List[Dict[str, Any]] = [
    {
        "title": "Python Official Tutorial & Language Reference",
        "url": "https://docs.python.org/3/tutorial/",
        "skill_tag": "Python",
        "resource_type": "Documentation",
        "description": "Comprehensive guide to Python syntax, standard library, data structures, and best practices."
    },
    {
        "title": "MDN Web Docs - JavaScript Guide",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "skill_tag": "JavaScript",
        "resource_type": "Documentation",
        "description": "In-depth guide covering JavaScript core features, async programming, and DOM APIs."
    },
    {
        "title": "TypeScript Handbook (Official Docs)",
        "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
        "skill_tag": "TypeScript",
        "resource_type": "Documentation",
        "description": "The definitive guide to types, interfaces, generics, and compiler options in TypeScript."
    },
    {
        "title": "React Official Documentation - Learn React",
        "url": "https://react.dev/learn",
        "skill_tag": "React",
        "resource_type": "Interactive",
        "description": "Hands-on tutorials explaining state, props, hooks, component lifecycle, and thinking in React."
    },
    {
        "title": "FastAPI Official Tutorial & User Guide",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "skill_tag": "FastAPI",
        "resource_type": "Documentation",
        "description": "Step-by-step tutorial covering request validation with Pydantic, dependency injection, and async routes."
    },
    {
        "title": "Docker Getting Started Guide",
        "url": "https://docs.docker.com/get-started/",
        "skill_tag": "Docker",
        "resource_type": "Tutorial",
        "description": "Hands-on walk-through to containerize applications, manage images, and compose multi-container setups."
    },
    {
        "title": "Kubernetes Basics Tutorial",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "skill_tag": "Kubernetes",
        "resource_type": "Tutorial",
        "description": "Interactive modules explaining pods, deployments, services, scaling, and rolling updates."
    },
    {
        "title": "PostgreSQL Tutorial for Beginners & Developers",
        "url": "https://www.postgresqltutorial.com/",
        "skill_tag": "PostgreSQL",
        "resource_type": "Tutorial",
        "description": "Practical guides to relational schema design, indexing, foreign keys, constraints, and query tuning."
    },
    {
        "title": "PyTorch Official Deep Learning Tutorials",
        "url": "https://pytorch.org/tutorials/",
        "skill_tag": "PyTorch",
        "resource_type": "Tutorial",
        "description": "Official guides from tensor basics to training custom deep neural networks and transfer learning."
    },
    {
        "title": "Hugging Face NLP & Transformers Course",
        "url": "https://huggingface.co/learn/nlp-course",
        "skill_tag": "NLP",
        "resource_type": "Course",
        "description": "Free course covering tokenizers, BERT, sentence transformers, fine-tuning, and text classification."
    },
    {
        "title": "FAISS GitHub Wiki & Getting Started Guide",
        "url": "https://github.com/facebookresearch/faiss/wiki/Getting-started",
        "skill_tag": "FAISS",
        "resource_type": "Documentation",
        "description": "Technical documentation on index types, Euclidean vs Cosine distance, and high-performance vector search."
    },
    {
        "title": "Sentence Transformers Documentation (SBERT)",
        "url": "https://sbert.net/",
        "skill_tag": "Sentence Transformers",
        "resource_type": "Documentation",
        "description": "Guides for computing dense vector representations of sentences and documents for semantic search."
    },
    {
        "title": "Scikit-Learn Machine Learning in Python",
        "url": "https://scikit-learn.org/stable/user_guide.html",
        "skill_tag": "Scikit-Learn",
        "resource_type": "Documentation",
        "description": "Detailed guides on supervised learning, classification, regression, clustering, and model validation."
    },
    {
        "title": "Tailwind CSS Official Documentation",
        "url": "https://tailwindcss.com/docs",
        "skill_tag": "Tailwind CSS",
        "resource_type": "Documentation",
        "description": "Utility-first CSS framework documentation covering layout, flexbox, grid, and dark mode."
    },
    {
        "title": "OWASP Top Ten Web Application Security Risks",
        "url": "https://owasp.org/www-project-top-ten/",
        "skill_tag": "Cybersecurity",
        "resource_type": "Documentation",
        "description": "Standard awareness document detailing common web vulnerabilities, injection defenses, and access control."
    },
    {
        "title": "Git Official Documentation & Book",
        "url": "https://git-scm.com/book/en/v2",
        "skill_tag": "Git",
        "resource_type": "Documentation",
        "description": "Complete reference for branching, merging, rebasing, and collaborating using Git."
    },
    {
        "title": "DeepLearning.AI Prompt Engineering for Developers",
        "url": "https://www.deeplearning.ai/short-courses/chatgpt-prompt-eng/",
        "skill_tag": "LLMs",
        "resource_type": "Course",
        "description": "Best practices for prompting, structured output formatting, and tool-augmented agent workflows."
    }
]
