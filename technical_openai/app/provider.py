import json
import os
from openai import OpenAI
from .prompt import TRIAGE_SYSTEM_PROMPT
from .schemas import TriageRequest

def triage_issue(req: TriageRequest) -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    user_prompt = f"""
Issue title: {req.title}
Service: {req.service_name}

Description:
{req.description}

Logs:
{req.logs}

Changed files:
{", ".join(req.changed_files) if req.changed_files else "N/A"}
"""

    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return json.loads(resp.choices[0].message.content)