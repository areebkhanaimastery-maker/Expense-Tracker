"""
Backend FastAPI API Integration Tests.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "HEALTHY"


def test_api_categories():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Food" in data["data"]
    assert "Shopping" in data["data"]


def test_api_expenses_crud():
    # 1. Create Expense
    payload = {
        "amount": 1250.50,
        "category": "Food",
        "description": "API Test Lunch",
        "date": "2026-08-13",
    }
    create_resp = client.post("/api/expenses", json=payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()["data"]
    expense_id = created_data["id"]
    assert created_data["amount"] == 1250.50
    assert created_data["category"] == "Food"

    # 2. Get Expense
    get_resp = client.get(f"/api/expenses/{expense_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["description"] == "API Test Lunch"

    # 3. Update Expense
    update_payload = {"amount": 1500.00, "description": "API Test Deluxe Lunch"}
    put_resp = client.put(f"/api/expenses/{expense_id}", json=update_payload)
    assert put_resp.status_code == 200
    assert put_resp.json()["data"]["amount"] == 1500.00

    # 4. Search Expense
    search_resp = client.get("/api/search?query=Deluxe")
    assert search_resp.status_code == 200
    assert len(search_resp.json()["data"]) >= 1

    # 5. Delete Expense
    del_resp = client.delete(f"/api/expenses/{expense_id}")
    assert del_resp.status_code == 200

    # 6. Verify Deletion
    get_missing = client.get(f"/api/expenses/{expense_id}")
    assert get_missing.status_code == 404


def test_api_analytics_summary():
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_spending" in data["data"]
    assert "category_totals" in data["data"]


def test_api_intelligence_profile_and_budget():
    profile_resp = client.get("/api/intelligence/profile")
    assert profile_resp.status_code == 200
    assert profile_resp.json()["success"] is True

    budget_resp = client.get("/api/intelligence/budget")
    assert budget_resp.status_code == 200
    assert budget_resp.json()["success"] is True


def test_api_intelligence_scenario():
    payload = {"category": "Shopping", "change_value": -20.0, "is_percentage": True}
    response = client.post("/api/intelligence/scenario", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["category"] == "Shopping"


def test_api_ml_anomalies_and_predictions():
    anomalies_resp = client.get("/api/ml/anomalies")
    assert anomalies_resp.status_code == 200
    assert anomalies_resp.json()["success"] is True

    pred_resp = client.get("/api/ml/predictions")
    assert pred_resp.status_code == 200
    assert pred_resp.json()["success"] is True


def test_api_ai_status_and_chat():
    status_resp = client.get("/api/ai/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["success"] is True

    chat_payload = {"message": "How much did I spend this month?"}
    chat_resp = client.post("/api/ai/chat", json=chat_payload)
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert data["success"] is True
    assert len(data["data"]["reply"]) > 10


def test_api_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json()["success"] is True
