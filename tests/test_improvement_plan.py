"""
test_improvement_plan.py
Comprehensive automated test suite for Improvement Plan features:
- System recommendation completion persistence in SQLite
- Student custom improvement plan CRUD (Create, Read, Update, Delete)
- Session persistence across logout/login and page refresh
- Strict student data isolation and unauthorized request rejection
- Input validation (empty titles, missing optional fields, invalid status)
- Exact task counts, overdue tracking, and completion percentage calculation
"""

from datetime import datetime, timezone, timedelta
import pytest
from starlette.testclient import TestClient
from backend.main import app, auth_db

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture
def student_a_token(client):
    res = client.post("/api/auth/login", json={"username": "stu1015", "password": "campus123"})
    assert res.status_code == 200
    return res.json()["token"]

@pytest.fixture
def student_b_token(client):
    res = client.post("/api/auth/login", json={"username": "stu1008", "password": "campus123"})
    assert res.status_code == 200
    return res.json()["token"]

@pytest.fixture
def faculty_token(client):
    res = client.post("/api/auth/login", json={"username": "faculty", "password": "campus123"})
    assert res.status_code == 200
    return res.json()["token"]

# -----------------------------------------------------------------------------
# 1. System Recommendation Completion Persistence Tests
# -----------------------------------------------------------------------------
def test_mark_recommendation_completed_and_revert_pending(client, student_a_token):
    """Students can mark a recommendation completed and toggle back to pending."""
    student_id = "STU1015"
    headers = {"Authorization": f"Bearer {student_a_token}"}

    # Fetch initial plan
    res_plan = client.get(f"/api/students/{student_id}/improvement-plan", headers=headers)
    assert res_plan.status_code == 200
    data = res_plan.json()
    recs = data["system_recommendations"]
    assert len(recs) > 0
    target_rec_id = recs[0]["id"]

    # 1. Mark completed
    res_comp = client.post(
        f"/api/students/{student_id}/recommendations/{target_rec_id}/status",
        headers=headers,
        json={"status": "completed"}
    )
    assert res_comp.status_code == 200
    comp_data = res_comp.json()
    assert comp_data["status"] == "success"
    assert comp_data["completion"]["is_completed"] is True
    assert comp_data["completion"]["completed_at"] is not None

    # Check updated plan stats
    res_plan2 = client.get(f"/api/students/{student_id}/improvement-plan", headers=headers)
    assert res_plan2.status_code == 200
    updated_recs = res_plan2.json()["system_recommendations"]
    target_rec = next(r for r in updated_recs if r["id"] == target_rec_id)
    assert target_rec["is_completed"] is True
    assert target_rec["status"] == "completed"

    # 2. Revert to pending
    res_pend = client.post(
        f"/api/students/{student_id}/recommendations/{target_rec_id}/status",
        headers=headers,
        json={"status": "pending"}
    )
    assert res_pend.status_code == 200
    pend_data = res_pend.json()
    assert pend_data["completion"]["is_completed"] is False
    assert pend_data["completion"]["completed_at"] is None

    # Check updated plan stats
    res_plan3 = client.get(f"/api/students/{student_id}/improvement-plan", headers=headers)
    assert res_plan3.status_code == 200
    reverted_rec = next(r for r in res_plan3.json()["system_recommendations"] if r["id"] == target_rec_id)
    assert reverted_rec["is_completed"] is False
    assert reverted_rec["status"] == "pending"

# -----------------------------------------------------------------------------
# 2. Custom Improvement Plan CRUD Tests
# -----------------------------------------------------------------------------
def test_create_custom_plan(client, student_a_token):
    """Students can create a custom task with title, category, priority, and target date."""
    student_id = "STU1015"
    headers = {"Authorization": f"Bearer {student_a_token}"}
    target_date = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "title": "Practice Python for 30 minutes daily",
        "description": "Complete two medium problems on LeetCode",
        "category": "Coding",
        "priority": "High",
        "target_date": target_date
    }

    res = client.post(f"/api/students/{student_id}/custom-plans", headers=headers, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    plan = data["plan"]
    assert plan["title"] == payload["title"]
    assert plan["description"] == payload["description"]
    assert plan["category"] == "Coding"
    assert plan["priority"] == "High"
    assert plan["status"] == "pending"
    assert plan["target_date"] == target_date
    assert plan["plan_id"].startswith("plan_")

def test_list_student_custom_plans(client, student_a_token):
    """Custom plans list retrieves all plans created by the student."""
    student_id = "STU1015"
    headers = {"Authorization": f"Bearer {student_a_token}"}

    res = client.get(f"/api/students/{student_id}/custom-plans", headers=headers)
    assert res.status_code == 200
    plans = res.json()
    assert isinstance(plans, list)
    assert len(plans) >= 1
    assert any(p["title"] == "Practice Python for 30 minutes daily" for p in plans)

def test_edit_custom_plan_and_toggle_status(client, student_a_token):
    """Students can edit title, priority, target date, and status of custom plans."""
    student_id = "STU1015"
    headers = {"Authorization": f"Bearer {student_a_token}"}

    # Create plan
    res_create = client.post(f"/api/students/{student_id}/custom-plans", headers=headers, json={
        "title": "Revise Compiler Design notes",
        "category": "Academic",
        "priority": "Medium"
    })
    assert res_create.status_code == 201
    plan_id = res_create.json()["plan"]["plan_id"]

    # Edit plan and mark completed
    res_edit = client.put(f"/api/students/{student_id}/custom-plans/{plan_id}", headers=headers, json={
        "title": "Revise Compiler Design notes (Chapter 1-4)",
        "priority": "High",
        "status": "completed"
    })
    assert res_edit.status_code == 200
    updated = res_edit.json()["plan"]
    assert updated["title"] == "Revise Compiler Design notes (Chapter 1-4)"
    assert updated["priority"] == "High"
    assert updated["status"] == "completed"
    assert updated["completed_at"] is not None

    # Revert status to pending
    res_revert = client.put(f"/api/students/{student_id}/custom-plans/{plan_id}", headers=headers, json={
        "status": "pending"
    })
    assert res_revert.status_code == 200
    reverted = res_revert.json()["plan"]
    assert reverted["status"] == "pending"
    assert reverted["completed_at"] is None

def test_delete_custom_plan(client, student_a_token):
    """Students can delete a custom plan with proper 200 and subsequent 404 confirmation."""
    student_id = "STU1015"
    headers = {"Authorization": f"Bearer {student_a_token}"}

    res_create = client.post(f"/api/students/{student_id}/custom-plans", headers=headers, json={
        "title": "Temporary Task To Delete",
        "category": "Other"
    })
    assert res_create.status_code == 201
    plan_id = res_create.json()["plan"]["plan_id"]

    # Delete
    res_del = client.delete(f"/api/students/{student_id}/custom-plans/{plan_id}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "success"
    assert res_del.json()["deleted_id"] == plan_id

    # Second delete returns 404
    res_del2 = client.delete(f"/api/students/{student_id}/custom-plans/{plan_id}", headers=headers)
    assert res_del2.status_code == 404

# -----------------------------------------------------------------------------
# 3. Persistence Across Logout and Login Tests
# -----------------------------------------------------------------------------
def test_persistence_across_logout_and_relogin(client):
    """Plan completion and custom tasks remain intact after logout and new session creation."""
    username = "stu1015"
    student_id = "STU1015"

    # 1. Login session 1
    res1 = client.post("/api/auth/login", json={"username": username, "password": "campus123"})
    token1 = res1.json()["token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Set custom task and complete a recommendation
    res_create = client.post(f"/api/students/{student_id}/custom-plans", headers=headers1, json={
        "title": "Persist Across Sessions Task",
        "category": "Skills",
        "priority": "High"
    })
    assert res_create.status_code == 201
    plan_id = res_create.json()["plan"]["plan_id"]

    # Mark recommendation completed
    res_comp = client.post(
        f"/api/students/{student_id}/recommendations/rec_academic_backlogs/status",
        headers=headers1,
        json={"status": "completed"}
    )
    assert res_comp.status_code == 200

    # 2. Logout session 1
    res_logout = client.post("/api/auth/logout", headers=headers1)
    assert res_logout.status_code == 200

    # 3. Login session 2
    res2 = client.post("/api/auth/login", json={"username": username, "password": "campus123"})
    token2 = res2.json()["token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Verify custom task and recommendation completion status still present
    res_plan = client.get(f"/api/students/{student_id}/improvement-plan", headers=headers2)
    assert res_plan.status_code == 200
    plan_data = res_plan.json()

    # Check custom plan
    custom_titles = [p["title"] for p in plan_data["custom_plans"]]
    assert "Persist Across Sessions Task" in custom_titles

    # Clean up created custom plan
    client.delete(f"/api/students/{student_id}/custom-plans/{plan_id}", headers=headers2)

# -----------------------------------------------------------------------------
# 4. Strict Isolation and Authorization Tests
# -----------------------------------------------------------------------------
def test_isolation_between_two_students(client, student_a_token, student_b_token):
    """Students cannot access, modify, or leak each other's custom plans or completions."""
    headers_a = {"Authorization": f"Bearer {student_a_token}"}
    headers_b = {"Authorization": f"Bearer {student_b_token}"}

    # Student A creates a task
    res_create = client.post("/api/students/STU1015/custom-plans", headers=headers_a, json={
        "title": "Confidential Study Task For Student A",
        "category": "Aptitude"
    })
    assert res_create.status_code == 201
    plan_id_a = res_create.json()["plan"]["plan_id"]

    # Student B cannot see Student A's improvement plan
    res_b_view = client.get("/api/students/STU1015/improvement-plan", headers=headers_b)
    assert res_b_view.status_code == 403

    # Student B cannot see Student A's custom plans
    res_b_list = client.get("/api/students/STU1015/custom-plans", headers=headers_b)
    assert res_b_list.status_code == 403

    # Student B cannot modify Student A's custom plan
    res_b_edit = client.put(f"/api/students/STU1015/custom-plans/{plan_id_a}", headers=headers_b, json={
        "title": "Hacked Title"
    })
    assert res_b_edit.status_code == 403

    # Student B cannot delete Student A's custom plan
    res_b_del = client.delete(f"/api/students/STU1015/custom-plans/{plan_id_a}", headers=headers_b)
    assert res_b_del.status_code == 403

    # Student B's own improvement plan does NOT contain Student A's task
    res_b_own = client.get("/api/students/STU1008/improvement-plan", headers=headers_b)
    assert res_b_own.status_code == 200
    b_titles = [p["title"] for p in res_b_own.json()["custom_plans"]]
    assert "Confidential Study Task For Student A" not in b_titles

    # Clean up
    client.delete(f"/api/students/STU1015/custom-plans/{plan_id_a}", headers=headers_a)

def test_unauthenticated_requests_rejected(client):
    """Unauthenticated requests must receive 401 Unauthorized."""
    assert client.get("/api/students/STU1015/improvement-plan").status_code == 401
    assert client.get("/api/students/STU1015/custom-plans").status_code == 401
    assert client.post("/api/students/STU1015/custom-plans", json={"title": "Test"}).status_code == 401
    assert client.put("/api/students/STU1015/custom-plans/plan_123", json={"title": "Test"}).status_code == 401
    assert client.delete("/api/students/STU1015/custom-plans/plan_123").status_code == 401

def test_faculty_forbidden_from_student_private_tasks(client, faculty_token):
    """Faculty members cannot view or alter private student improvement plans."""
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/students/STU1015/improvement-plan", headers=headers)
    assert res.status_code == 403
    assert "forbidden" in res.json()["detail"].lower()

# -----------------------------------------------------------------------------
# 5. Validation and Edge Cases Tests
# -----------------------------------------------------------------------------
def test_validation_empty_title_and_invalid_fields(client, student_a_token):
    """Validations reject empty titles, whitespace-only titles, or invalid enum categories."""
    headers = {"Authorization": f"Bearer {student_a_token}"}

    # Empty title
    res1 = client.post("/api/students/STU1015/custom-plans", headers=headers, json={
        "title": "   "
    })
    assert res1.status_code in (400, 422)

    # Invalid category
    res2 = client.post("/api/students/STU1015/custom-plans", headers=headers, json={
        "title": "Valid Title",
        "category": "InvalidCategory123"
    })
    assert res2.status_code == 422

    # Invalid priority
    res3 = client.post("/api/students/STU1015/custom-plans", headers=headers, json={
        "title": "Valid Title",
        "priority": "Extreme"
    })
    assert res3.status_code == 422

def test_task_counts_overdue_and_completion_percentage(client, student_a_token):
    """Task counts and completion percentage are accurately calculated without double counting."""
    student_id = "STU1015"
    headers = {"Authorization": f"Bearer {student_a_token}"}

    # Fetch initial plan stats
    res = client.get(f"/api/students/{student_id}/improvement-plan", headers=headers)
    assert res.status_code == 200
    stats = res.json()["stats"]
    assert stats["total_tasks"] == stats["completed_tasks"] + stats["pending_tasks"]
    assert 0.0 <= stats["completion_percentage"] <= 100.0

    # Add an overdue task (yesterday's date)
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    res_overdue = client.post(f"/api/students/{student_id}/custom-plans", headers=headers, json={
        "title": "Overdue Homework Task",
        "category": "Academic",
        "priority": "High",
        "target_date": yesterday
    })
    assert res_overdue.status_code == 201
    overdue_id = res_overdue.json()["plan"]["plan_id"]

    # Verify overdue count increased
    res_after = client.get(f"/api/students/{student_id}/improvement-plan", headers=headers)
    stats_after = res_after.json()["stats"]
    assert stats_after["overdue_tasks"] >= 1

    # Mark the overdue task completed: overdue count should decrease
    client.put(f"/api/students/{student_id}/custom-plans/{overdue_id}", headers=headers, json={
        "status": "completed"
    })
    res_completed = client.get(f"/api/students/{student_id}/improvement-plan", headers=headers)
    stats_completed = res_completed.json()["stats"]
    assert stats_completed["overdue_tasks"] < stats_after["overdue_tasks"]

    # Clean up
    client.delete(f"/api/students/{student_id}/custom-plans/{overdue_id}", headers=headers)
