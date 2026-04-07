import os
import sys
from openai import OpenAI

if len(sys.argv) != 2:
    raise SystemExit("usage: python scripts/generate_requirements.py <stakeholder_notes.md>")

notes = open(sys.argv[1], "r", encoding="utf-8").read()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

prompt = f"""
Convert these stakeholder notes into a concise PRD in Markdown.

Required sections:
- Problem statement
- Users
- Goals
- Non-goals
- Functional requirements
- Non-functional requirements
- Risks
- Acceptance criteria
- KPIs
- Rollout plan

Stakeholder notes:
{notes}
"""

resp = client.chat.completions.create(
    model=model,
    temperature=0.2,
    messages=[
        {"role": "system", "content": "You are a product manager and delivery lead."},
        {"role": "user", "content": prompt},
    ],
)

print(resp.choices[0].message.content)