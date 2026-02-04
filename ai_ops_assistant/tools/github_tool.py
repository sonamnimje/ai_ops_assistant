import os
from typing import Any, Dict, List

import requests


GITHUB_API_URL = "https://api.github.com"


def _request_with_retries(url: str, headers: Dict[str, str], params: Dict[str, str] | None = None) -> requests.Response:
    last_exc: Exception | None = None
    for _ in range(3):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response
            if response.status_code in {400, 401, 403, 404}:
                return response
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    if last_exc:
        raise last_exc
    raise RuntimeError("request failed without exception")


def _auth_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_repo_details(repo_full_name: str) -> Dict[str, Any]:
    headers = _auth_headers()
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}"
    response = _request_with_retries(url, headers)
    if response.status_code != 200:
        return {"error": f"GitHub API returned {response.status_code}", "details": response.text}
    data = response.json()
    return {
        "name": data.get("full_name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "language": data.get("language"),
        "html_url": data.get("html_url"),
    }


def search_repositories(keyword: str, per_page: int = 3) -> Dict[str, Any]:
    headers = _auth_headers()
    url = f"{GITHUB_API_URL}/search/repositories"
    params = {"q": keyword, "per_page": str(per_page), "sort": "stars", "order": "desc"}
    response = _request_with_retries(url, headers, params=params)
    if response.status_code != 200:
        return {"error": f"GitHub API returned {response.status_code}", "details": response.text}
    data = response.json()
    items: List[Dict[str, Any]] = []
    for repo in data.get("items", []):
        items.append(
            {
                "name": repo.get("full_name"),
                "stars": repo.get("stargazers_count"),
                "html_url": repo.get("html_url"),
            }
        )
    return {"items": items}
