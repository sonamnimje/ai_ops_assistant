# AI Operations Assistant

Local multi-agent assistant that plans tasks, executes real API calls (GitHub + OpenWeather), and verifies results using an LLM.

## Features
- Planner → Executor → Verifier pipeline
- Real GitHub REST and OpenWeather API calls via `requests`
- LLM used only for reasoning (planning + verification)
- CLI runnable in VS Code terminal
- Environment-based configuration with `.env`

## Quickstart
1. Python 3.10+.
2. Create env file:
   ```bash
   # AI Operations Assistant
   A **CLI-based multi-agent AI Operations Assistant** that converts natural language tasks into executable plans, calls real third-party APIs (GitHub + OpenWeather), and verifies results using an LLM.

   The system demonstrates **agent-based reasoning**, **tool orchestration**, and **real API integration**, all running locally.

   ---

   ## Features

   - Multi-agent architecture: **Planner → Executor → Verifier**
   - LLM-powered planning and verification (no monolithic prompts)
   - Real GitHub REST API integration
   - Real OpenWeather API integration
   - Fully **CLI-based** (no localhost server)
   - Environment-based configuration using `.env`
   - Runs locally in VS Code / terminal

   ---

   ## Tech Stack

   - Python 3.10+
   - OpenAI-compatible LLM
   - GitHub REST API
   - OpenWeather API
   - `requests`, `python-dotenv`

   ---

   ## Project Structure

   ai_ops_assistant/
   ├── agents/
   │ ├── planner.py
   │ ├── executor.py
   │ └── verifier.py
   ├── tools/
   │ ├── github_tool.py
   │ └── weather_tool.py
   ├── llm/
   │ └── llm_client.py
   ├── main.py
   ├── requirements.txt
   ├── .env.example
   └── README.md

   ---

   ## Setup Instructions

   ### 1. Prerequisites
   - Python **3.10 or higher**
   - VS Code or any terminal

   ---

   ### 2. Create virtual environment

   ```bash
   python -m venv .venv
   ```


   Activate:

   Windows (PowerShell)

   ```
   .venv\Scripts\Activate.ps1
   ```


   macOS / Linux

   ```
   source .venv/bin/activate
   ```

   3. Configure environment variables
   cp .env.example .env


   Fill in .env:

   ```
   OPENAI_API_KEY=sk-your-key
   OPENAI_MODEL=gpt-4o-mini

   # Optional
   # OPENAI_BASE_URL=https://api.yourprovider.com/v1
   # GITHUB_TOKEN=ghp_your_token

   OPENWEATHER_API_KEY=your_openweather_key
   ```

   4. Install dependencies
   ```
   pip install -r requirements.txt
   ```

   Running the Application (CLI)

   ⚠️ This project runs entirely as a CLI application.
   There is no localhost server or HTTP endpoint.

   Navigate to the project directory:

   ```
   cd ai_ops_assistant
   ```


   Run with a task:

   ```
   python main.py \
     --task "Find top 3 Python GitHub repositories and show current weather in Mumbai" \
     --location "Mumbai" \
     --units metric
   ```

   Sample Task
   Find top 3 Python GitHub repositories and show current weather in Mumbai

   What Happens Internally

   Planner Agent

   Uses an LLM to convert the user request into a strict JSON execution plan

   Selects appropriate tools (GitHub search, Weather lookup)

   Executor Agent

   Executes each step

   Calls real GitHub and OpenWeather APIs

   Verifier Agent

   Validates completeness

   Handles partial failures

   Formats the final response

   Final Output

   Printed directly to the terminal

   Expected Output

   Generated JSON execution plan

   Live GitHub repository data

   Real-time weather data

   Verified and structured final summary

   Troubleshooting

   Module not found → Ensure virtual environment is activated

   Invalid API key → Recheck .env

   Weather not found → Ensure city name is valid

   GitHub rate limit error → Add GITHUB_TOKEN to .env

   Notes

   GitHub token is optional but recommended to avoid rate limits

   OpenWeather API key is required for weather lookups

   Lightweight retries and graceful fallbacks are implemented

   Designed intentionally as CLI-first per assignment requirements

   Optional Enhancements (Future Work)

   FastAPI wrapper for HTTP endpoint

   Parallel tool execution

   Response caching

   Cost tracking per LLM request

   Streamlit-based UI
