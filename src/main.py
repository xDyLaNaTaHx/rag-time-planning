import json
import os
import re

import chromadb
from dotenv import load_dotenv

from src.llm import send_prompt
from src.schemas import WeeklySchedule

load_dotenv()

SCHEDULE_SYSTEM_PROMPT = """You are a helpful calendar assistant.
Given the user's goals and constraints, propose a realistic weekly schedule.

Respond with ONLY valid JSON matching this schema:
{
  "blocks": [
    {
      "day": "Monday",
      "start_time": "09:00",
      "end_time": "10:00",
      "activity": "string",
      "linked_goal": "string",
      "priority": 1
    }
  ],
  "rationale": "string explaining the schedule"
}

Rules:
- Use days Monday through Sunday.
- Use 24-hour HH:MM times.
- Respect all constraints (busy times, sleep, work, commute).
- Link each block to a relevant goal when possible.
- priority is an integer from 1 (highest) to 5 (lowest).
- Do not schedule over constrained busy periods.
"""


def _extract_json(text: str) -> dict:
    """Parse JSON from a model response, tolerating markdown fences."""
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    return json.loads(cleaned)


def generate_schedule_response(
    goals: list[str],
    constraints: list[str],
    query: str = "How should I schedule my week?",
) -> WeeklySchedule:
    documents = [f"Goal: {g}" for g in goals] + [
        f"Constraint: {c}" for c in constraints
    ]
    if not documents:
        documents = ["No goals or constraints provided."]

    chroma_client = chromadb.Client()
    collection_name = "user-support"
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=collection_name)
    collection.add(
        ids=[str(i) for i in range(len(documents))],
        documents=documents,
    )

    n_results = min(len(documents), 8)
    results = collection.query(query_texts=[query], n_results=n_results)
    context = "\n".join(results["documents"][0])

    prompt = (
        f"{query}\n\n"
        f"Retrieved context:\n{context}\n\n"
        f"All goals:\n" + "\n".join(f"- {g}" for g in goals) + "\n\n"
        f"All constraints:\n" + "\n".join(f"- {c}" for c in constraints)
    )

    raw = send_prompt(
        model=os.getenv("AI_MODEL"),
        messages=[
            {"role": "system", "content": SCHEDULE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        json_mode=True,
    )

    data = _extract_json(raw)
    return WeeklySchedule.model_validate(data)
