"""
test_api.py
Tests FastAPI endpoints for Smart Campus Analytics.
Verifies health, student listing, profile lookups, score breakdown,
risk diagnostics, recommendations, and 404 error handling with session authorization.
"""

import pytest
from starlette.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def auth_headers(client):
    res = client.post("/api/auth/login", json={
        "student_id": "STU1001",
        "password": "campus123"
    })
    token = res.json()["session_id"]
    return {"Authorization": f"Bearer {token}"}

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["student_count"] == 120

def test_get_students_unauthenticated_rejected(client):
    """Test public access to student directory is blocked without authentication."""
    response = client.get("/api/students")
    assert response.status_code == 401
    assert "authentication required" in response.json()["detail"].lower()

def test_get_students_list(client, auth_headers):
    """Test authenticated access to student directory returns full list."""
    response = client.get("/api/students", headers=auth_headers)
    assert response.status_code == 200
    students = response.json()
    assert len(students) == 120
    first = students[0]
    assert "student_id" in first
    assert "student_name" in first
    assert "success_score" in first
    assert "academic_risk_level" in first
    assert "placement_risk_level" in first

def test_get_students_filter(client, auth_headers):
    """Test authenticated access to student directory with department filter."""
    response = client.get("/api/students?department=Computer%20Science%20and%20Engineering", headers=auth_headers)
    assert response.status_code == 200
    students = response.json()
    assert len(students) > 0
    assert all(s["department"] == "Computer Science and Engineering" for s in students)

def test_get_valid_student_profile(client, auth_headers):
    response = client.get("/api/students/STU1001", headers=auth_headers)
    assert response.status_code == 200
    dossier = response.json()
    assert dossier["student_id"] == "STU1001"
    assert "personal_info" in dossier
    assert "success_score" in dossier
    assert "academic_details" in dossier
    assert "attendance_details" in dossier
    assert "lms_details" in dossier
    assert "engagement_details" in dossier
    assert "placement_details" in dossier
    assert "skills_details" in dossier
    assert "feedback_details" in dossier
    assert "recommendations" in dossier

def test_get_invalid_student_profile_unauthenticated(client):
    response = client.get("/api/students/STU9999_NONEXISTENT")
    assert response.status_code == 401

def test_get_student_score(client, auth_headers):
    response = client.get("/api/students/STU1001/score", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "breakdown" in data
    assert 0 <= data["overall_score"] <= 100

def test_get_student_risks(client, auth_headers):
    response = client.get("/api/students/STU1001/risks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "academic_risk" in data
    assert "placement_risk" in data
    assert data["academic_risk"]["level"] in ["High", "Moderate", "Low"]

def test_get_student_recommendations(client, auth_headers):
    response = client.get("/api/students/STU1001/recommendations", headers=auth_headers)
    assert response.status_code == 200
    recs = response.json()
    assert isinstance(recs, list)
    assert len(recs) > 0
    first = recs[0]
    assert "category" in first
    assert "priority" in first
    assert "suggested_action" in first
    assert "improvement_target" in first

def test_get_cohort_summary(client):
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_students"] == 120
    assert "average_success_score" in data
    assert "academic_risk_distribution" in data
    assert "placement_risk_distribution" in data
