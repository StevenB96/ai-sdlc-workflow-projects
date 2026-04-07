import os
import sys
from openai import OpenAI

if len(sys.argv) != 2:
    raise SystemExit("usage: python scripts/generate_architecture.py <requirements.md>")

prd = open(sys.argv[1], "r", encoding="utf-8").read()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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

resp = client.chat.completions.create(
    model=model,
    temperature=0.2,
    messages=[
        {"role": "system", "content": "You are a staff engineer writing an architecture doc."},
        {"role": "user", "content": prompt},
    ],
)

print(resp.choices[0].message.content)