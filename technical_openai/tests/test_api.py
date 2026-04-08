from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "AI Incident Triage API"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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

    response = client.post("/triage", json=payload)
    assert response.status_code == 200
    assert response.json()["severity"] == "high"
    assert response.json()["probable_component"] == "backend"
