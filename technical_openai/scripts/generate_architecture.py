import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if len(sys.argv) != 2:
    raise SystemExit(
        "usage: python scripts/generate_architecture.py <requirements.md>")

prd = open(sys.argv[1], "r", encoding="utf-8").read()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=api_key)

prompt = f"""
Based on this PRD, write a lightweight architecture document in Markdown.

Required sections:
- Overview
- Components
- API contract
- Data flow
- Failure modes and mitigations
- Test strategy
- Rollout and rollback
- Mermaid diagram

PRD:
{prd}
"""

response = client.chat.completions.create(
    model=model,
    temperature=0.2,
    messages=[
        {"role": "system", "content": "You are a staff engineer writing an architecture document."},
        {"role": "user", "content": prompt},
    ],
)

print(response.choices[0].message.content)
