import json
from typing import Any, Dict, List

from llm.llm_client import LLMClient


class VerifierAgent:
    """Validates execution artifacts and formats final output via LLM."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client

    def _build_prompt(self, task: str, plan: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        template = (
            "You are a Verifier Agent.\n"
            "Responsibilities:\n"
            "- Validate that each planned step was executed successfully.\n"
            "- If any step failed, clearly mention it.\n"
            "- Summarize results in a clear, structured, human-readable format.\n"
            "Output rules:\n"
            "- If GitHub search results are present, list repository name and star count.\n"
            "- If weather data is present, summarize city, temperature, and conditions.\n"
            "- Do NOT mention internal agent names or fallback messages.\n"
            "- Produce a clean final answer suitable for end users or evaluators.\n"
            "Return ONLY markdown with sections: Summary, GitHub, Weather, Issues.\n"
            "Be concise. No speculative claims."
        )
        return (
            f"{template}\n"
            f"User task: {task}\n"
            f"Plan JSON: {json.dumps(plan, ensure_ascii=False)}\n"
            f"Results JSON: {json.dumps(results, ensure_ascii=False)}"
        )

    def verify(self, task: str, plan: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        prompt = self._build_prompt(task, plan, results)
        try:
            return self.llm.chat(prompt)
        except Exception:
            return self._fallback(results)

    def _fallback(self, results: List[Dict[str, Any]]) -> str:
        summary: List[str] = ["Summary: Results processed."]
        github_lines: List[str] = []
        weather_lines: List[str] = []
        issue_lines: List[str] = []

        for entry in results:
            res = entry.get("result", {})
            if "error" in res:
                issue_lines.append(f"Step {entry.get('step_id')}: {res['error']}")
                continue
            if entry.get("tool") == "github_search":
                items = res.get("items", [])
                if items:
                    for repo in items:
                        name = repo.get("name")
                        stars = repo.get("stars")
                        github_lines.append(f"{name} (⭐ {stars})")
            if entry.get("tool") == "github":
                name = res.get("name")
                stars = res.get("stars")
                if name:
                    github_lines.append(f"{name} (⭐ {stars})")
            if entry.get("tool") == "weather":
                city = res.get("city")
                temp = res.get("temperature")
                cond = res.get("conditions")
                if city:
                    weather_lines.append(f"{city}: {temp}°C, {cond}")

        parts = ["Summary"] + summary
        parts.append("\nGitHub")
        parts.extend(github_lines or ["No GitHub data."])
        parts.append("\nWeather")
        parts.extend(weather_lines or ["No weather data."])
        if issue_lines:
            parts.append("\nIssues")
            parts.extend(issue_lines)
        return "\n".join(parts)


def build_verifier(llm_client: LLMClient) -> VerifierAgent:
    return VerifierAgent(llm_client)
