import json
from typing import Any, Dict, List

from llm.llm_client import LLMClient


PLANNER_PROMPT = (
    "You are a Planner Agent in a CLI-based multi-agent system.\n"
    "Convert the user's request into a step-by-step JSON plan.\n\n"
    "STRICT RULES:\n"
    "- Output ONLY valid JSON.\n"
    "- Include ALL required steps from the user request.\n"
    "- Do NOT omit steps.\n"
    "- Do NOT fetch a single GitHub repository unless explicitly named.\n\n"
    "GITHUB RULES:\n"
    "- If the user asks for \"top\", \"best\", or \"popular\" repositories, use GitHub search.\n"
    "- Tool: \"github_search\" with input { \"query\": \"<query>\", \"limit\": <number> }.\n\n"
    "WEATHER RULES (MANDATORY):\n"
    "- If the user asks for weather AND mentions a city name, extract the city exactly as written.\n"
    "- Do NOT invent or replace the city.\n"
    "- Tool: \"weather\" with input { \"city\": \"<city_from_user>\", \"units\": \"metric\" }.\n\n"
    "PLAN FORMAT:\n"
    "{\n  \"steps\": [\n    {\n      \"step_id\": 1,\n      \"action\": \"<description>\",\n      \"tool\": \"<tool_name>\",\n      \"input\": { ... }\n    }\n  ]\n}\n"
)


class PlannerAgent:
    """Generates a JSON execution plan using an LLM."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client

    def _build_prompt(self, task: str, location: str | None) -> str:
        location_text = f"Location: {location}" if location else "Location: not provided"
        return f"{PLANNER_PROMPT}\nTask: {task}\n{location_text}"

    def _fallback_plan(self, task: str, location: str | None) -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = []
        lowered = task.lower()
        step_id = 1

        # ---- Detect "top / best / popular"
        top_like = any(word in lowered for word in ["top", "best", "popular", "most starred"])

        # ---- Detect explicit repo
        explicit_repo = None
        for token in task.replace(",", " ").split():
            if "/" in token and len(token.split("/")) == 2:
                explicit_repo = token.strip()
                break

        # ---- GitHub logic
        if top_like:
            query = "language:Python" if "python" in lowered else task
            steps.append(
                {
                    "step_id": step_id,
                    "action": "search repositories",
                    "tool": "github_search",
                    "input": {"query": query, "limit": 3},
                }
            )
            step_id += 1

        elif explicit_repo:
            steps.append(
                {
                    "step_id": step_id,
                    "action": "fetch repository details",
                    "tool": "github",
                    "input": {"repo_full_name": explicit_repo},
                }
            )
            step_id += 1

        elif any(word in lowered for word in ["repo", "github", "git"]):
            steps.append(
                {
                    "step_id": step_id,
                    "action": "search repositories",
                    "tool": "github_search",
                    "input": {"query": task, "limit": 3},
                }
            )
            step_id += 1

        # ---- Weather intent
        weather_intent = any(word in lowered for word in ["weather", "temperature", "climate"])

        # ---- Extract city from task if location not provided
        city = location
        if not city:
            words = task.split()
            for i, w in enumerate(words):
                if w.lower() in ["in", "at", "for"] and i + 1 < len(words):
                    city = words[i + 1].strip(",.")
                    break

        # ---- Weather step (MANDATORY if city + intent)
        if weather_intent and city:
            steps.append(
                {
                    "step_id": step_id,
                    "action": "get weather",
                    "tool": "weather",
                    "input": {"city": city, "units": "metric"},
                }
            )
            step_id += 1

        # ---- Default fallback
        if not steps:
            steps.append(
                {
                    "step_id": step_id,
                    "action": "search repositories",
                    "tool": "github_search",
                    "input": {"query": task, "limit": 3},
                }
            )

        return {"steps": steps}

    def create_plan(self, task: str, location: str | None = None) -> Dict[str, Any]:
        prompt = self._build_prompt(task, location)
        try:
            response = self.llm.chat(prompt)
        except Exception:
            return self._fallback_plan(task, location)

        try:
            plan = json.loads(response)
            if not isinstance(plan, dict) or "steps" not in plan:
                raise ValueError("Plan missing steps")
            return plan
        except Exception:
            return self._fallback_plan(task, location)


def build_planner(llm_client: LLMClient) -> PlannerAgent:
    return PlannerAgent(llm_client)
