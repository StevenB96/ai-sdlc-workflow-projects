import os
import sys
from openai import OpenAI

if len(sys.argv) != 2:
    raise SystemExit("usage: python scripts/review_diff.py <diff_file>")

diff = open(sys.argv[1], "r", encoding="utf-8").read()[:120000]
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

prompt = f"""
Review this git diff like a senior software engineer.

Focus on:
- correctness
- breaking changes
- security
- missing tests
- readability
- rollback risk

Return Markdown with sections:
- Summary
- Blocking Issues
- Suggestions
- Missing Tests

Diff:
{diff}
"""

resp = client.chat.completions.create(
    model=model,
    temperature=0.1,
    messages=[
        {"role": "system", "content": "You are a strict but practical code reviewer."},
        {"role": "user", "content": prompt},
    ],
)

print(resp.choices[0].message.content)