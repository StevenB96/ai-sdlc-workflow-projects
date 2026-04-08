import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from .prompt import TRIAGE_SYSTEM_PROMPT
from .schemas import TriageRequest

load_dotenv()


def triage_issue(req: TriageRequest) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    user_prompt = f"""
Issue title: {req.title}
Service: {req.service_name}

Description:
{req.description}

Logs:
{req.logs or "N/A"}

Changed files:
{", ".join(req.changed_files) if req.changed_files else "N/A"}
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Model returned empty content")

    return json.loads(content)
