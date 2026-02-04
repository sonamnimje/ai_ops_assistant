import argparse
import json
from typing import Any, Dict, List

from dotenv import load_dotenv

from agents.planner import build_planner
from agents.executor import build_executor
from agents.verifier import build_verifier
from llm.llm_client import LLMClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Operations Assistant")
    parser.add_argument("--task", required=True, help="User task description")
    parser.add_argument("--location", help="City for weather lookup", default=None)
    parser.add_argument("--units", help="Weather units (metric or imperial)", default="metric")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    llm_client = LLMClient()
    planner = build_planner(llm_client)
    executor = build_executor()
    verifier = build_verifier(llm_client)

    plan = planner.create_plan(args.task, args.location)

    # Inject units into weather steps if user set it explicitly
    for step in plan.get("steps", []):
        if step.get("tool") == "weather" and args.units:
            step.setdefault("params", {})["units"] = args.units

    results = executor.execute(plan)

    final_output = verifier.verify(args.task, plan, results)

    print("Plan:\n" + json.dumps(plan, indent=2))
    print("\nResults:\n" + json.dumps(results, indent=2))
    print("\nFinal Output:\n" + final_output)


if __name__ == "__main__":
    main()
