import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if len(sys.argv) != 2:
    raise SystemExit(
        "usage: python scripts/generate_requirements.py <stakeholder_notes.md>")

notes = open(sys.argv[1], "r", encoding="utf-8").read()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=api_key)

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

response = client.chat.completions.create(
    model=model,
    temperature=0.2,
    messages=[
        {"role": "system", "content": "You are a product manager and delivery lead."},
        {"role": "user", "content": prompt},
    ],
)

print(response.choices[0].message.content)
