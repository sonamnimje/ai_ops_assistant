# AI Ops Assistant

CLI multi-agent assistant that plans tasks, runs external tools, and verifies results using an OpenAI-compatible model. Current tools include GitHub repo search/details and OpenWeather current conditions.

## How It Works
- Planner builds a JSON plan from the user task using the LLM with guarded prompts and a deterministic fallback ([ai_ops_assistant/agents/planner.py](ai_ops_assistant/agents/planner.py)).
- Executor runs steps sequentially by dispatching to registered tools ([ai_ops_assistant/agents/executor.py](ai_ops_assistant/agents/executor.py)).
- Verifier validates outcomes and formats a user-facing markdown answer via LLM with a graceful fallback formatter ([ai_ops_assistant/agents/verifier.py](ai_ops_assistant/agents/verifier.py)).
- LLM client wraps OpenAI-compatible chat completions ([ai_ops_assistant/llm/llm_client.py](ai_ops_assistant/llm/llm_client.py)).

## Prerequisites
- Python 3.10+
- pip and virtualenv recommended
- API keys: `OPENAI_API_KEY` (required), `OPENWEATHER_API_KEY` (for weather), `GITHUB_TOKEN` (optional but avoids rate limits)

## Setup
1) Install dependencies:
```bash
pip install -r ai_ops_assistant/requirements.txt
```
2) Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1        # optional, override if using a proxy
OPENAI_MODEL=gpt-4o-mini                         # optional
OPENWEATHER_API_KEY=your_openweather_key
GITHUB_TOKEN=ghp_your_token                      # optional
```

## Run
Execute from the repo root:
```bash
python -m ai_ops_assistant.main --task "find top python data viz repos"
python -m ai_ops_assistant.main --task "weather in Paris" --location "Paris" --units metric
python -m ai_ops_assistant.main --task "analyze repo" --location "London" --units imperial
```
Flags:
- `--task` (required): natural language request.
- `--location` (optional): city name; also auto-inferred for weather if task contains "in/at/for <city>".
- `--units` (optional): `metric` or `imperial`; injected into weather steps when provided.

## Behavior Notes
- Planner enforces JSON-only plans and applies heuristics for GitHub search vs explicit repo lookup; weather steps are mandatory when intent and city are present.
- Executor tool map currently supports `github`, `github_search`, and `weather` with basic parameter validation.
- Verifier summarizes GitHub stars and weather conditions, and reports failures when tools error.
- Network calls retry on transient failures and surface API status codes in errors.

## Extending
- Add tools in [ai_ops_assistant/tools](ai_ops_assistant/tools) and register them in [ai_ops_assistant/agents/executor.py](ai_ops_assistant/agents/executor.py).
- Adjust prompt/policy in [ai_ops_assistant/agents/planner.py](ai_ops_assistant/agents/planner.py) or verifier template in [ai_ops_assistant/agents/verifier.py](ai_ops_assistant/agents/verifier.py).
- Swap models or endpoints via `OPENAI_BASE_URL`/`OPENAI_MODEL` in `.env`.

## Troubleshooting
- Missing keys: ensure `.env` is loaded or env vars are exported before running.
- GitHub 403/404: check `GITHUB_TOKEN` scope or rate limits.
- Weather errors: validate city spelling and `OPENWEATHER_API_KEY`.

## Example Output (truncated)
```
Plan:
{
	"steps": [
		{"step_id": 1, "action": "search repositories", "tool": "github_search", "input": {"query": "top python data viz", "limit": 3}}
	]
}

Results:
[
	{"step_id": 1, "tool": "github_search", "result": {"items": [{"name": "plotly/plotly.py", "stars": 150000}]}}
]

Final Output:
Summary
- Found popular Python data visualization repositories.

GitHub
- plotly/plotly.py (⭐ 150000)

Weather
- No weather data.
```
