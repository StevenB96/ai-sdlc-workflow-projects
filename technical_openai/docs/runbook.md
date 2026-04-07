# Runbook

## Health check
GET /health should return 200.

## Common failures
1. 401/403 -> API key missing or invalid
2. 500 with JSON parsing error -> inspect raw model output, tighten prompt, add regression test
3. Latency spike -> switch to smaller model or reduce prompt size

## Rollback
- Revert last commit
- Merge fix or redeploy previous Render version

## Escalation
- Open incident issue
- Attach logs
- Add failing sample to data/eval_cases.jsonl