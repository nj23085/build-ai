from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_safety_demo_returns_structured_findings(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "demo")
    response = client.post("/api/analyze/safety", json={
        "description": "Worker near an unprotected roof edge without a harness",
        "weather": "clear",
        "site_context": "roof work"
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "demo"
    assert len(body["findings"]) >= 1
    assert "severity" in body["findings"][0]

def test_planning_estimate():
    response = client.post("/api/planning/estimate", json={
        "area_sqft": 1200, "floors": 1, "finish_level": "standard", "location": "Indore"
    })
    assert response.status_code == 200
    body = response.json()
    assert body["total_area_sqft"] == 1200
    assert body["indicative_cost_high_inr"] > body["indicative_cost_low_inr"]

def test_invalid_planning_rejected():
    response = client.post("/api/planning/estimate", json={
        "area_sqft": -1, "floors": 1, "finish_level": "standard", "location": "Indore"
    })
    assert response.status_code == 422

def test_valuation():
    response = client.post("/api/valuation/estimate", json={
        "area_sqft": 1000, "rate_per_sqft_inr": 4000, "age_years": 5, "condition": "good"
    })
    assert response.status_code == 200
    assert response.json()["estimated_value_inr"] > 0

def test_assistant():
    response = client.post("/api/assistant", json={"question": "What should I check for site safety?"})
    assert response.status_code == 200
    assert "answer" in response.json()


def test_assistant_work_at_height_gives_specific_guidance(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "demo")

    response = client.post(
        "/api/assistant",
        json={
            "question": "What should I check before starting work at height?",
            "site_context": "Second-floor construction work",
            "weather": "Clear",
        },
    )

    assert response.status_code == 200
    data = response.json()
    answer = data["answer"].lower()

    assert any(
        term in answer
        for term in ["scaffold", "fall-protection", "guardrails"]
    )
    assert "rescue" in answer
