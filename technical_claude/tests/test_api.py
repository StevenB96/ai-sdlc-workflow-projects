from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_triage(monkeypatch):
    import app.main as main_module

    def fake_triage(_req):
        return {
            "severity": "high",
            "probable_component": "backend",
            "root_cause_hypothesis": "Null pointer after deploy",
            "recommended_fix": "Add null check and redeploy",
            "test_plan": ["Add unit test for missing payload", "Verify in staging"],
            "rollback_plan": "Roll back the most recent release",
            "release_note": "Improved API stability for failed requests.",
            "confidence": 0.84,
        }

    monkeypatch.setattr(main_module, "triage_issue", fake_triage)

    payload = {
        "title": "Users see 500 after deploy",
        "description": "Login endpoint returns 500 for some users",
        "logs": "AttributeError: 'NoneType' object has no attribute 'id'",
        "changed_files": ["api/login.py"],
        "service_name": "auth-service",
    }

    r = client.post("/triage", json=payload)
    assert r.status_code == 200
    assert r.json()["severity"] == "high"
    assert r.json()["probable_component"] == "backend"
