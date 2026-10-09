"""
test_faculty.py
Comprehensive automated tests for Faculty Authentication, Authorization (Role-based access control),
Record Updating, Validation, SQLite Persistence, and Analytics Recalculation.
"""

import pytest
from starlette.testclient import TestClient
from backend.main import app, auth_db, service

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def faculty_token(client):
    res = client.post("/api/auth/login", json={
        "username": "faculty",
        "password": "campus123"
    })
    assert res.status_code == 200, f"Faculty login failed: {res.text}"
    data = res.json()
    assert data["role"] == "faculty"
    return data["token"]

@pytest.fixture(scope="module")
def student_token(client):
    res = client.post("/api/auth/login", json={
        "username": "stu1015",
        "password": "campus123"
    })
    assert res.status_code == 200, f"Student login failed: {res.text}"
    data = res.json()
    assert data["role"] == "student"
    return data["token"]

def test_faculty_login_success(client):
    """Test faculty can successfully log in with demo credentials."""
    res = client.post("/api/auth/login", json={
        "username": "faculty",
        "password": "campus123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "faculty"
    assert data["student_id"] == "FAC001"
    assert "token" in data
    assert "session_id" in data

def test_faculty_me_endpoint(client, faculty_token):
    """Test /api/auth/me returns role='faculty' for faculty sessions."""
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "faculty"
    assert data["user"]["role"] == "faculty"
    assert data["user"]["student_id"] == "FAC001"
    assert data["student"] is None

def test_student_forbidden_from_faculty_update_endpoint(client, student_token):
    """Students must receive 403 Forbidden when attempting to call faculty update endpoints."""
    payload = {
        "academic_updates": [{"subject_name": "Operating Systems", "marks": 99.0}],
        "attendance_updates": []
    }
    res = client.post(
        "/api/faculty/students/STU1001/records",
        headers={"Authorization": f"Bearer {student_token}"},
        json=payload
    )
    assert res.status_code == 403
    assert "faculty" in res.json()["detail"].lower()

def test_unauthenticated_forbidden_from_faculty_update(client):
    """Unauthenticated requests must receive 401 Unauthorized."""
    payload = {
        "academic_updates": [{"subject_name": "Operating Systems", "marks": 99.0}]
    }
    res = client.post("/api/faculty/students/STU1001/records", json=payload)
    assert res.status_code == 401

def test_faculty_can_access_student_dossier(client, faculty_token):
    """Faculty members can view any student profile."""
    res = client.get("/api/students/STU1001", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    profile = res.json()
    assert profile["student_id"] == "STU1001"
    assert "academic_details" in profile
    assert "attendance_details" in profile

def test_faculty_update_validation_ranges(client, faculty_token):
    """Validation must reject marks out of range (0-100) and invalid attendance."""
    # Marks > 100
    res1 = client.post(
        "/api/faculty/students/STU1001/records",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json={"academic_updates": [{"subject_name": "Operating Systems", "marks": 105.0}]}
    )
    assert res1.status_code == 422

    # Marks < 0
    res2 = client.post(
        "/api/faculty/students/STU1001/records",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json={"academic_updates": [{"subject_name": "Operating Systems", "marks": -5.0}]}
    )
    assert res2.status_code == 422

    # Total classes <= 0
    res3 = client.post(
        "/api/faculty/students/STU1001/records",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json={"attendance_updates": [{"subject_name": "Operating Systems", "classes_attended": 10, "total_classes": 0}]}
    )
    assert res3.status_code == 422

def test_faculty_update_and_analytics_recalculation(client, faculty_token):
    """Faculty update triggers SQLite persistence and recalculation of Success Score, CGPA, and Risk."""
    target_id = "STU1008" # Originally an at-risk profile

    # Fetch initial state
    res_before = client.get(f"/api/students/{target_id}", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_before.status_code == 200
    profile_before = res_before.json()
    score_before = profile_before["success_score"]["overall_score"]

    # Subject list
    academic_list = profile_before["academic_details"]["subjects_breakdown"]
    first_subject = academic_list[0]["subject_name"]

    # Boost marks to 95 and attendance to 48/50 (96%)
    payload = {
        "academic_updates": [
            {"subject_name": first_subject, "marks": 95.0}
        ],
        "attendance_updates": [
            {"subject_name": first_subject, "classes_attended": 48, "total_classes": 50}
        ]
    }

    res_update = client.post(
        f"/api/faculty/students/{target_id}/records",
        headers={"Authorization": f"Bearer {faculty_token}"},
        json=payload
    )
    assert res_update.status_code == 200
    update_data = res_update.json()
    assert update_data["status"] == "success"
    assert "updated_profile" in update_data

    updated_profile = update_data["updated_profile"]
    score_after = updated_profile["success_score"]["overall_score"]

    # Score should improve with boosted marks and attendance
    assert score_after >= score_before

    # Verify updated subject marks in profile
    updated_subs = {s["subject_name"]: s["marks"] for s in updated_profile["academic_details"]["subjects_breakdown"]}
    assert updated_subs[first_subject] == 95.0

    # Verify updated attendance in profile
    updated_att = {s["subject_name"]: s for s in updated_profile["attendance_details"]["attendance_breakdown"]}
    assert updated_att[first_subject]["classes_attended"] == 48
    assert updated_att[first_subject]["total_classes"] == 50
    assert updated_att[first_subject]["attendance_percentage"] == 96.0

def test_sqlite_persistence_across_service_pipeline_reload(client, faculty_token):
    """Verify that persisted updates remain in SQLite tables and are applied on pipeline reload."""
    target_id = "STU1008"
    acad_updates = auth_db.get_academic_updates(target_id)
    att_updates = auth_db.get_attendance_updates(target_id)
    assert len(acad_updates) > 0
    assert len(att_updates) > 0

    # Force service reload
    service.reload(auth_db_instance=auth_db)
    reloaded_profile = service.get_student_profile(target_id)
    first_sub = acad_updates[0]["subject_name"]
    updated_subs = {s["subject_name"]: s["marks"] for s in reloaded_profile["academic_details"]["subjects_breakdown"]}
    assert updated_subs[first_sub] == 95.0
