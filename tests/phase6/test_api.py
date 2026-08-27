import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_system_status():
    response = client.get("/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "python_version" in data
    assert data["reporting_available"] is True

def test_investigation_not_found():
    response = client.get("/investigations/invalid-id")
    assert response.status_code == 404
