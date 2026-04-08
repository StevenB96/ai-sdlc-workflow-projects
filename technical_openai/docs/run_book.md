# Runbook

## Purpose
This service provides AI-assisted incident triage for sample engineering issues.

## Health check
- `GET /health` should return `200` with `{"status": "ok"}`

## Common failures
1. `401` or `403`
   - API key missing or invalid
   - Check `.env` locally or GitHub Secrets in CI

2. `500` with JSON parsing error
   - Inspect raw provider output
   - Tighten the prompt
   - Add a regression case to `data/eval_cases.jsonl`

3. Latency spike
   - Retry later
   - Use a smaller model
   - Reduce prompt size

## Rollback
- Revert the last commit
- Re-run tests
- Rebuild the Docker image

## Operational notes
- Never send secrets or customer PII to the model
- Treat outputs as draft recommendations only
- Add new failure examples to the evaluation dataset