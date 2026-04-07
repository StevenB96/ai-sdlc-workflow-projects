import json
import sys
import time
import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

with open("data/eval_cases.jsonl", "r", encoding="utf-8") as f:
    cases = [json.loads(line) for line in f if line.strip()]

severity_hits = 0
component_hits = 0
latencies = []
failures = []

for case in cases:
    start = time.perf_counter()
    r = requests.post(f"{BASE_URL}/triage", json=case["input"], timeout=90)
    elapsed = time.perf_counter() - start
    latencies.append(elapsed)

    r.raise_for_status()
    pred = r.json()
    expected = case["expected"]

    severity_ok = pred["severity"] == expected["severity"]
    component_ok = pred["probable_component"] == expected["probable_component"]

    severity_hits += int(severity_ok)
    component_hits += int(component_ok)

    if not (severity_ok and component_ok):
        failures.append({
            "title": case["input"]["title"],
            "predicted": {
                "severity": pred["severity"],
                "probable_component": pred["probable_component"],
            },
            "expected": expected,
        })

summary = {
    "cases": len(cases),
    "severity_accuracy": round(severity_hits / len(cases), 3) if cases else 0,
    "component_accuracy": round(component_hits / len(cases), 3) if cases else 0,
    "avg_latency_seconds": round(sum(latencies) / len(latencies), 3) if latencies else 0,
    "failures": failures,
}

print(json.dumps(summary, indent=2))
