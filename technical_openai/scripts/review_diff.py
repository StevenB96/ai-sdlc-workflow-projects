import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if len(sys.argv) != 2:
    raise SystemExit("usage: python scripts/review_diff.py <diff_file>")

diff = open(sys.argv[1], "r", encoding="utf-8").read()[:120000]

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=api_key)

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

response = client.chat.completions.create(
    model=model,
    temperature=0.1,
    messages=[
        {"role": "system", "content": "You are a strict but practical code reviewer."},
        {"role": "user", "content": prompt},
    ],
)

print(response.choices[0].message.content)
