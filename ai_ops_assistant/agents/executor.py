from typing import Any, Callable, Dict, List

from tools.github_tool import fetch_repo_details, search_repositories
from tools.weather_tool import fetch_current_weather


class ExecutorAgent:
    """Runs plan steps sequentially using registered tools."""

    def __init__(self) -> None:
        self.tool_map: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "github": self._run_github,
            "github_search": self._run_github_search,
            "weather": self._run_weather,
        }

    def _run_github(self, params: Dict[str, Any]) -> Dict[str, Any]:
        repo_full_name = params.get("repo_full_name")
        if not repo_full_name:
            return {"error": "missing repo_full_name"}
        return fetch_repo_details(repo_full_name)

    def _run_github_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query")
        if not query:
            return {"error": "missing query"}
        limit = params.get("limit", 3)
        return search_repositories(keyword=query, per_page=int(limit))

    def _run_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        city = params.get("city")
        if not city:
            return {"error": "missing city"}
        units = params.get("units", "metric")
        return fetch_current_weather(city=city, units=units)

    def execute(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for step in plan.get("steps", []):
            tool_name = step.get("tool")
            params = step.get("input", {})
            handler = self.tool_map.get(tool_name)
            step_id = step.get("step_id")
            if not handler:
                results.append({"step_id": step_id, "error": f"unknown tool {tool_name}"})
                continue
            try:
                outcome = handler(params)
            except Exception as exc:  # noqa: BLE001
                outcome = {"error": str(exc)}
            results.append({
                "step_id": step_id,
                "tool": tool_name,
                "action": step.get("action"),
                "result": outcome,
            })
        return results


def build_executor() -> ExecutorAgent:
    return ExecutorAgent()
