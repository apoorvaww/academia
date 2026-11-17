import re
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.config import AGENT_MAX_ITERATIONS, AGENT_MAX_QUERY_LENGTH
from app.models.entities import Student
from app.agent.tools import AVAILABLE_TOOLS
from app.models.schemas import AgentToolCallLog, AgentChatResponse
from app.agent.llm_provider import get_llm_provider, GeminiProvider

logger = logging.getLogger(__name__)

REACT_SYSTEM_PROMPT = """You are an AI Career Advisory Agent for the Academia-Industry Portal.
Your task is to help university students find matching internships, analyze their skill gaps against real job requirements, and formulate grounded learning plans.

You have access to the following 3 tools:
1. search_internships: {"query": "string (required)", "skill_filters": ["string"], "work_mode": "string", "max_results": int}
2. analyze_skill_gap: {"internship_id": int (required)}
3. create_learning_plan: {"missing_skills": ["string"] (required), "target_role": "string", "time_budget_weeks": int}

You must strictly follow this ReAct format:
Thought: Describe your reasoning about what step to take next.
Action: [tool_name]
Action Input: [Valid JSON object matching tool parameters]
Observation: [The tool result will be supplied here]

When you have enough information to answer the student's request, provide your final response in this format:
Thought: I now have all the required verified facts.
Final Answer: [Detailed, grounded, and encouraging explanation based strictly on the tool observations. Do not invent fake internships or fake external submission links.]
"""

def sanitize_query(query: str) -> str:
    """Sanitize query against malicious prompt injection and excessive length."""
    if not query:
        return ""
    cleaned = query.strip()[:AGENT_MAX_QUERY_LENGTH]
    # Neutralize injection attempts that try to override the system instructions
    cleaned = re.sub(r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions?", "[filtered]", cleaned)
    cleaned = re.sub(r"(?i)system\s*:", "[system_tag_filtered]", cleaned)
    return cleaned

def execute_react_deterministic(db: Session, student_id: int, query: str) -> AgentChatResponse:
    """
    Deterministic multi-step ReAct engine that parses intent and executes the registered
    tools with full Thought/Action/Observation logging.
    """
    start_time = time.time()
    tool_logs: List[AgentToolCallLog] = []
    evidence: Dict[str, Any] = {}

    query_lower = query.lower()

    # Detect student profile
    student = db.query(Student).filter(Student.id == student_id).first()
    target_role = (student.target_role if student and student.target_role else "Software Engineer")

    # Determine intent
    wants_search = any(kw in query_lower for kw in ["search", "find", "internship", "recommend", "roles", "jobs", "opportunities", "what can i apply"])
    wants_gap = any(kw in query_lower for kw in ["gap", "missing", "lack", "qualif", "readiness", "prepare", "fit"])
    wants_plan = any(kw in query_lower for kw in ["plan", "learn", "roadmap", "curriculum", "study", "resource", "course", "how to improve"])

    # If general greeting or unspecific query, default to helpful search + analysis
    if not (wants_search or wants_gap or wants_plan):
        wants_search = True
        wants_gap = True

    # Multi-step execution step 1: Search internships
    best_internship_id = None
    if wants_search or wants_gap:
        # Extract search query
        extracted_query = target_role
        if "ml" in query_lower or "machine learning" in query_lower:
            extracted_query = "Machine Learning"
        elif "frontend" in query_lower or "react" in query_lower:
            extracted_query = "Frontend Developer"
        elif "backend" in query_lower or "api" in query_lower:
            extracted_query = "Backend Developer"
        elif "data" in query_lower:
            extracted_query = "Data Science"
        elif "devops" in query_lower or "cloud" in query_lower:
            extracted_query = "DevOps"

        t0 = time.time()
        search_args = {"query": extracted_query, "max_results": 3}
        search_result = AVAILABLE_TOOLS["search_internships"]["function"](db, student_id, search_args)
        duration = round((time.time() - t0) * 1000, 2)

        results = search_result.get("results", [])
        evidence["search_results"] = results
        tool_logs.append(AgentToolCallLog(
            tool_name="search_internships",
            tool_args=search_args,
            observation_summary=f"Retrieved {len(results)} matching internships for query '{extracted_query}'. Top match: {results[0]['title'] if results else 'None'}.",
            duration_ms=duration
        ))

        if results:
            best_internship_id = results[0]["id"]

    # Multi-step execution step 2: Analyze Skill Gap
    missing_skills: List[str] = []
    if (wants_gap or wants_plan) and best_internship_id:
        t0 = time.time()
        gap_args = {"internship_id": best_internship_id}
        gap_result = AVAILABLE_TOOLS["analyze_skill_gap"]["function"](db, student_id, gap_args)
        duration = round((time.time() - t0) * 1000, 2)

        missing_skills = gap_result.get("missing_required_skills", [])
        evidence["skill_gap"] = gap_result
        tool_logs.append(AgentToolCallLog(
            tool_name="analyze_skill_gap",
            tool_args=gap_args,
            observation_summary=f"Analyzed skill gap for internship #{best_internship_id}. Matched: {gap_result.get('matched_required_skills')}. Missing: {missing_skills}.",
            duration_ms=duration
        ))

    # Multi-step execution step 3: Create Learning Plan
    if (wants_plan or missing_skills) and missing_skills:
        t0 = time.time()
        plan_args = {
            "missing_skills": missing_skills,
            "target_role": target_role,
            "time_budget_weeks": 4
        }
        plan_result = AVAILABLE_TOOLS["create_learning_plan"]["function"](db, student_id, plan_args)
        duration = round((time.time() - t0) * 1000, 2)

        evidence["learning_plan"] = plan_result
        tool_logs.append(AgentToolCallLog(
            tool_name="create_learning_plan",
            tool_args=plan_args,
            observation_summary=f"Generated {plan_result.get('total_weeks')}-week learning plan covering: {', '.join(missing_skills)} with verified resources.",
            duration_ms=duration
        ))

    # Formulate grounded response
    response_sections = []
    if "search_results" in evidence and evidence["search_results"]:
        top_picks = evidence["search_results"]
        response_sections.append(
            f"### 🎯 Top Matching Opportunities\n"
            f"Based on your profile and target goals, I found **{len(top_picks)} relevant internships** in our database:\n"
        )
        for item in top_picks:
            response_sections.append(
                f"- **{item['title']}** at *{item['company']}* ({item['work_mode'].capitalize()}) — **{item['fit_percentage']} Fit Score**\n"
                f"  - *Matched Skills:* {', '.join(item['matched_required']) if item['matched_required'] else 'Foundational'}\n"
                f"  - *Notes:* {item['explanation']}\n"
            )

    if "skill_gap" in evidence:
        gap = evidence["skill_gap"]
        response_sections.append(
            f"\n### 📊 Skill Gap Analysis for {gap.get('title')}\n"
            f"- **Readiness Level:** {gap.get('readiness_level')}\n"
            f"- **Confirmed Skills You Have:** {', '.join(gap.get('matched_required_skills', [])) or 'None recorded'}\n"
            f"- **Key Skills to Acquire:** {', '.join(gap.get('missing_required_skills', [])) or 'None! You meet all required skills.'}\n"
            f"- **Guidance:** {gap.get('actionable_guidance')}\n"
        )

    if "learning_plan" in evidence and evidence["learning_plan"].get("steps"):
        plan = evidence["learning_plan"]
        response_sections.append(
            f"\n### 📚 Recommended Actionable Learning Plan ({plan.get('total_weeks')} Weeks)\n"
        )
        for step in plan.get("steps", []):
            resource_links = ", ".join([f"[{r['title']}]({r['url']})" for r in step.get("resources", [])])
            response_sections.append(
                f"- **Week {step['week_number']} ({step['skill']}):** {step['action_item']}\n"
                f"  - *Hands-on Project:* {step['practice_project']}\n"
                f"  - *Verified Resources:* {resource_links}\n"
            )

    if not response_sections:
        response_sections.append(
            "I checked our internship database, but couldn't locate specific matches for that search. Try asking for roles like 'Machine Learning', 'Frontend Developer', or 'DevOps'!"
        )

    response_text = "\n".join(response_sections)
    return AgentChatResponse(
        response=response_text,
        tool_logs=tool_logs,
        grounded_evidence=evidence
    )

def run_agent_chat(db: Session, student_id: int, query: str) -> AgentChatResponse:
    """
    Main entrypoint for student AI Career Copilot. Uses Gemini if available,
    with automatic fail-safe to deterministic ReAct execution.
    """
    clean_q = sanitize_query(query)
    provider = get_llm_provider()

    # If Gemini Provider is active, attempt LLM ReAct loop
    if isinstance(provider, GeminiProvider):
        try:
            return run_react_llm_loop(db, student_id, clean_q, provider)
        except Exception as e:
            logger.error(f"Gemini ReAct execution error: {e}. Falling back to deterministic solver.")

    # Standard deterministic ReAct execution
    return execute_react_deterministic(db, student_id, clean_q)

def run_react_llm_loop(db: Session, student_id: int, query: str, provider: GeminiProvider) -> AgentChatResponse:
    """
    Runs bounded ReAct reasoning loop with an LLM provider.
    """
    tool_logs: List[AgentToolCallLog] = []
    evidence: Dict[str, Any] = {}
    conversation_history = f"Student Question: {query}\n"

    for iteration in range(AGENT_MAX_ITERATIONS):
        prompt = (
            f"{conversation_history}\n"
            f"Think step-by-step. What is your Thought? What Action do you take? Or are you ready for Final Answer?"
        )
        step_response = provider.generate_step(REACT_SYSTEM_PROMPT, prompt)
        
        # Check for Final Answer
        if "Final Answer:" in step_response:
            final_part = step_response.split("Final Answer:", 1)[1].strip()
            return AgentChatResponse(
                response=final_part,
                tool_logs=tool_logs,
                grounded_evidence=evidence
            )

        # Parse Action and Action Input
        action_match = re.search(r"Action:\s*(\w+)", step_response)
        input_match = re.search(r"Action Input:\s*(\{.*?\})", step_response, re.DOTALL)

        if not action_match or not input_match:
            # If model didn't follow tool format, return text or fallback
            break

        tool_name = action_match.group(1).strip()
        raw_input = input_match.group(1).strip()

        if tool_name not in AVAILABLE_TOOLS:
            observation = f"Error: Tool '{tool_name}' is not permitted. Allowed tools: {list(AVAILABLE_TOOLS.keys())}."
        else:
            try:
                args = json.loads(raw_input)
                t0 = time.time()
                tool_fn = AVAILABLE_TOOLS[tool_name]["function"]
                # Server-enforced student_id
                result = tool_fn(db, student_id, args)
                duration = round((time.time() - t0) * 1000, 2)
                observation = json.dumps(result)
                
                tool_logs.append(AgentToolCallLog(
                    tool_name=tool_name,
                    tool_args=args,
                    observation_summary=f"Executed {tool_name} successfully.",
                    duration_ms=duration
                ))
                evidence[tool_name] = result
            except Exception as e:
                observation = f"Tool execution failed: {str(e)}"

        conversation_history += f"\n{step_response}\nObservation: {observation}\n"

    # If loop ended without final answer, use deterministic formulation with evidence
    fallback = execute_react_deterministic(db, student_id, query)
    if tool_logs:
        fallback.tool_logs = tool_logs + fallback.tool_logs
    return fallback
