"""
test_auth.py
Automated tests for username-and-password authentication, session preservation,
logout, data isolation, and SQLite login history persistence.
"""

import os
import pytest
from starlette.testclient import TestClient
from backend.main import app, auth_db

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_login_with_valid_username_and_password(client):
    """Test login succeeds with valid username and password."""
    # Test with lowercase username
    response = client.post("/api/auth/login", json={
        "username": "stu1015",
        "password": "campus123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "session_id" in data
    assert data["student_id"] == "STU1015"
    assert data["username"] == "stu1015"
    assert data["status"] == "active"
    assert "login_timestamp" in data

    # Test with student ID format
    res_id = client.post("/api/auth/login", json={
        "username": "STU1015",
        "password": "campus123"
    })
    assert res_id.status_code == 200
    assert res_id.json()["student_id"] == "STU1015"

def test_login_with_incorrect_password(client):
    """Test login fails with incorrect password."""
    response = client.post("/api/auth/login", json={
        "username": "stu1015",
        "password": "wrong_password_999"
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_login_with_unknown_username(client):
    """Test login fails with unknown username."""
    response = client.post("/api/auth/login", json={
        "username": "unknown_student_9999",
        "password": "campus123"
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_login_with_empty_fields(client):
    """Test login validation for empty username or password."""
    # Empty username
    res1 = client.post("/api/auth/login", json={
        "username": "",
        "password": "campus123"
    })
    assert res1.status_code == 400
    assert "username is required" in res1.json()["detail"].lower()

    # Empty password
    res2 = client.post("/api/auth/login", json={
        "username": "stu1015",
        "password": ""
    })
    assert res2.status_code == 400
    assert "password is required" in res2.json()["detail"].lower()

def test_refreshing_dashboard_while_logged_in(client):
    """Test session validation and user restoration (equivalent to page refresh)."""
    # Authenticate to get session token
    login_res = client.post("/api/auth/login", json={
        "username": "stu1008",
        "password": "campus123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["token"]

    # Restore session via GET /api/auth/me using Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["student"]["student_id"] == "STU1008"
    assert data["student"]["personal_info"]["student_name"] == "Rhea Kumar"
    assert data["session"]["status"] == "active"
    assert data["session"]["session_id"] == token

def test_logging_out_and_logging_in_as_another_student(client):
    """Test logging out terminates the session and allows signing in as a different student."""
    # 1. Login as Student A (Naveen Das, STU1015)
    login_a = client.post("/api/auth/login", json={
        "username": "stu1015",
        "password": "campus123"
    })
    assert login_a.status_code == 200
    token_a = login_a.json()["token"]

    # Verify Student A profile
    me_a = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert me_a.status_code == 200
    assert me_a.json()["student"]["student_id"] == "STU1015"

    # 2. Logout Student A
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token_a}"})
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "logged_out"

    # 3. Verify Token A is now rejected
    after_logout = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert after_logout.status_code == 401

    # 4. Login as Student B (Surya Kumar, STU1002)
    login_b = client.post("/api/auth/login", json={
        "username": "stu1002",
        "password": "campus123"
    })
    assert login_b.status_code == 200
    token_b = login_b.json()["token"]

    # Verify Student B profile is returned
    me_b = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_b}"})
    assert me_b.status_code == 200
    assert me_b.json()["student"]["student_id"] == "STU1002"
    assert me_b.json()["student"]["personal_info"]["student_name"] == "Surya Kumar"

def test_blocking_dashboard_and_api_access_without_authentication(client):
    """Test all protected endpoints reject requests without a valid session."""
    endpoints = [
        "/api/auth/me",
        "/api/auth/history",
        "/api/students/STU1015",
        "/api/students/STU1015/score",
        "/api/students/STU1015/risks",
        "/api/students/STU1015/recommendations",
    ]

    for endpoint in endpoints:
        # Without header
        res_no_auth = client.get(endpoint)
        assert res_no_auth.status_code == 401, f"{endpoint} should require authentication"

        # With bogus header
        res_bad_auth = client.get(endpoint, headers={"Authorization": "Bearer bogus_invalid_token"})
        assert res_bad_auth.status_code == 401, f"{endpoint} should reject invalid token"

def test_preventing_one_student_from_accessing_another_students_information(client):
    """Test a logged-in student cannot access another student's dossier, score, risks, or recommendations."""
    # Login as STU1015
    login_res = client.post("/api/auth/login", json={
        "username": "stu1015",
        "password": "campus123"
    })
    token_1015 = login_res.json()["token"]

    # Own access allowed
    own_res = client.get("/api/students/STU1015", headers={"Authorization": f"Bearer {token_1015}"})
    assert own_res.status_code == 200
    assert own_res.json()["student_id"] == "STU1015"

    # Cross-student access forbidden (403)
    foreign_targets = [
        "/api/students/STU1008",
        "/api/students/STU1008/score",
        "/api/students/STU1008/risks",
        "/api/students/STU1008/recommendations",
    ]
    for target in foreign_targets:
        res = client.get(target, headers={"Authorization": f"Bearer {token_1015}"})
        assert res.status_code == 403, f"{target} should return 403 Forbidden for STU1015"
        assert "forbidden" in res.json()["detail"].lower()

def test_preserving_login_history_in_sqlite(client):
    """Test login audit trail persists in SQLite and is strictly isolated per student."""
    # Login as STU1036, then logout
    res1 = client.post("/api/auth/login", json={"username": "stu1036", "password": "campus123"})
    token1 = res1.json()["token"]
    client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token1}"})

    # Login as STU1036 again
    res2 = client.post("/api/auth/login", json={"username": "stu1036", "password": "campus123"})
    token2 = res2.json()["token"]

    # Retrieve history for STU1036
    history_res = client.get("/api/auth/history", headers={"Authorization": f"Bearer {token2}"})
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 2
    assert all(h["student_id"] == "STU1036" for h in history)
    assert any(h["status"] == "logged_out" for h in history)
    assert any(h["status"] == "active" for h in history)

    # Simulate backend restart by connecting a fresh AuthDatabase instance
    from src.auth_db import AuthDatabase
    restarted_db = AuthDatabase()
    restarted_history = restarted_db.get_student_login_history("STU1036")
    assert len(restarted_history) >= 2
    assert restarted_history[0]["student_id"] == "STU1036"

def test_login_creates_exactly_one_session_record(client):
    """Test every successful login creates exactly one new session record in SQLite."""
    # Count sessions for student before
    initial_history = auth_db.get_student_login_history("STU1090")
    initial_count = len(initial_history)

    # First login
    res1 = client.post("/api/auth/login", json={"username": "stu1090", "password": "campus123"})
    assert res1.status_code == 200
    token1 = res1.json()["token"]

    history_after_1 = auth_db.get_student_login_history("STU1090")
    assert len(history_after_1) == initial_count + 1
    assert history_after_1[0]["session_id"] == token1
    assert history_after_1[0]["status"] == "active"
    assert history_after_1[0]["logout_timestamp"] is None

    # Second login for same student
    res2 = client.post("/api/auth/login", json={"username": "stu1090", "password": "campus123"})
    assert res2.status_code == 200
    token2 = res2.json()["token"]

    history_after_2 = auth_db.get_student_login_history("STU1090")
    assert len(history_after_2) == initial_count + 2
    # Verify the first session is now concluded/logged_out
    first_sess = [h for h in history_after_2 if h["session_id"] == token1][0]
    assert first_sess["status"] == "logged_out"
    assert first_sess["logout_timestamp"] is not None
    # Verify the second session is the active one
    second_sess = [h for h in history_after_2 if h["session_id"] == token2][0]
    assert second_sess["status"] == "active"
    assert second_sess["logout_timestamp"] is None

    # Clean up by logging out
    client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token2}"})

def test_refresh_and_navigation_do_not_create_extra_records(client):
    """Test dashboard refreshes, API queries, and navigation create 0 extra records."""
    # Login
    login_res = client.post("/api/auth/login", json={"username": "stu1091", "password": "campus123"})
    assert login_res.status_code == 200
    token = login_res.json()["token"]

    initial_history = auth_db.get_student_login_history("STU1091")
    count_before = len(initial_history)

    # Simulate 5 page refreshes (/api/auth/me)
    for _ in range(5):
        res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200

    # Simulate navigating through all pages
    nav_endpoints = [
        "/api/students/STU1091",
        "/api/students/STU1091/score",
        "/api/students/STU1091/risks",
        "/api/students/STU1091/recommendations",
        "/api/auth/history",
    ]
    for ep in nav_endpoints:
        res = client.get(ep, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200

    # Verify session count has not increased AT ALL
    history_after = auth_db.get_student_login_history("STU1091")
    assert len(history_after) == count_before, "Page refreshes and navigation must not create extra session records"
    assert history_after[0]["session_id"] == token
    assert history_after[0]["status"] == "active"

    # Clean up by logging out
    client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})

def test_change_password_success_and_login_with_new_password(client):
    """Test successful password change, old password rejection, and login with new password."""
    # Ensure fresh demo password state
    auth_db.reset_password("stu1050", "campus123")

    # 1. Login with initial demo password
    login_res = client.post("/api/auth/login", json={
        "username": "stu1050",
        "password": "campus123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["token"]

    # 2. Change password with valid compliant password
    change_res = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {token}"}, json={
        "current_password": "campus123",
        "new_password": "NewStrong#Pass2026",
        "confirm_password": "NewStrong#Pass2026"
    })
    assert change_res.status_code == 200
    assert change_res.json()["status"] == "success"

    # 3. Old password must no longer work
    old_login = client.post("/api/auth/login", json={
        "username": "stu1050",
        "password": "campus123"
    })
    assert old_login.status_code == 401

    # 4. New password must authenticate successfully
    new_login = client.post("/api/auth/login", json={
        "username": "stu1050",
        "password": "NewStrong#Pass2026"
    })
    assert new_login.status_code == 200
    assert new_login.json()["student_id"] == "STU1050"

def test_change_password_incorrect_current_password(client):
    """Test change password fails when current password is wrong."""
    login_res = client.post("/api/auth/login", json={
        "username": "stu1051",
        "password": "campus123"
    })
    token = login_res.json()["token"]

    change_res = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {token}"}, json={
        "current_password": "wrong_current_password_999",
        "new_password": "Strong#Pass2026",
        "confirm_password": "Strong#Pass2026"
    })
    assert change_res.status_code == 400
    assert "incorrect current password" in change_res.json()["detail"].lower()

def test_change_password_weak_passwords_rejection(client):
    """Test all 5 password complexity conditions are strictly enforced."""
    login_res = client.post("/api/auth/login", json={
        "username": "stu1052",
        "password": "campus123"
    })
    token = login_res.json()["token"]

    weak_passwords = [
        ("Ab1!", "at least 8 characters"),
        ("weakpass123#", "uppercase"),
        ("WEAKPASS123#", "lowercase"),
        ("WeakPassword#", "number"),
        ("WeakPassword123", "special character"),
    ]

    for weak_pwd, expected_err in weak_passwords:
        res = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {token}"}, json={
            "current_password": "campus123",
            "new_password": weak_pwd,
            "confirm_password": weak_pwd
        })
        assert res.status_code == 400, f"Expected {weak_pwd} to be rejected"
        assert expected_err in res.json()["detail"].lower()

def test_change_password_mismatched_confirmation(client):
    """Test change password fails when new password and confirmation do not match."""
    login_res = client.post("/api/auth/login", json={
        "username": "stu1053",
        "password": "campus123"
    })
    token = login_res.json()["token"]

    change_res = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {token}"}, json={
        "current_password": "campus123",
        "new_password": "Strong#Pass2026",
        "confirm_password": "Different#Pass2026"
    })
    assert change_res.status_code == 400
    assert "not match" in change_res.json()["detail"].lower()

def test_change_password_unauthenticated_rejected(client):
    """Test change password requires active authenticated session."""
    # Without authorization header
    res_no_auth = client.post("/api/auth/change-password", json={
        "current_password": "campus123",
        "new_password": "Strong#Pass2026",
        "confirm_password": "Strong#Pass2026"
    })
    assert res_no_auth.status_code == 401

    # With invalid token
    res_bad_auth = client.post("/api/auth/change-password", headers={"Authorization": "Bearer bad_token"}, json={
        "current_password": "campus123",
        "new_password": "Strong#Pass2026",
        "confirm_password": "Strong#Pass2026"
    })
    assert res_bad_auth.status_code == 401

def test_change_password_persistence_and_no_overwrite_on_reinit(client):
    """Test changed password persists across backend restart and is not overwritten by seeding."""
    auth_db.reset_password("stu1054", "campus123")
    login_res = client.post("/api/auth/login", json={
        "username": "stu1054",
        "password": "campus123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["token"]

    # Change password
    change_res = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {token}"}, json={
        "current_password": "campus123",
        "new_password": "Restart#Pass2026",
        "confirm_password": "Restart#Pass2026"
    })
    assert change_res.status_code == 200

    # Simulate backend restart and re-seeding
    from src.auth_db import AuthDatabase
    restarted_db = AuthDatabase()
    restarted_db._seed_demo_users()  # Must NOT overwrite changed password

    # Verify authentication works with changed password in restarted DB
    user = restarted_db.authenticate_user("stu1054", "Restart#Pass2026")
    assert user is not None
    assert user["student_id"] == "STU1054"

    # Verify old password does NOT work
    old_user = restarted_db.authenticate_user("stu1054", "campus123")
    assert old_user is None

def test_change_password_user_isolation(client):
    """Test changing password for authenticated student does not alter other students' accounts."""
    # Login as Student A (STU1080)
    login_a = client.post("/api/auth/login", json={
        "username": "stu1080",
        "password": "campus123"
    })
    assert login_a.status_code == 200
    token_a = login_a.json()["token"]

    # Student A changes password
    change_a = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {token_a}"}, json={
        "current_password": "campus123",
        "new_password": "StudentA#Pass2026",
        "confirm_password": "StudentA#Pass2026"
    })
    assert change_a.status_code == 200

    # Student B (STU1081) must still be able to login with their initial demo password
    login_b = client.post("/api/auth/login", json={
        "username": "stu1081",
        "password": "campus123"
    })
    assert login_b.status_code == 200
    assert login_b.json()["student_id"] == "STU1081"

    # Reset stu1080 back to demo password
    auth_db.reset_password("stu1080", "campus123")
    auth_db.reset_password("stu1050", "campus123")
    auth_db.reset_password("stu1054", "campus123")

def test_password_hashes_stored_not_plaintext():
    """Verify passwords are saved as salted PBKDF2 hashes and never as plaintext."""
    import sqlite3
    conn = sqlite3.connect(auth_db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, username, password_hash, salt FROM users")
    users = cursor.fetchall()
    assert len(users) >= 100
    for u in users:
        # Passwords must NEVER be plaintext
        assert u["password_hash"] != "campus123"
        # PBKDF2-SHA256 hex string is 64 characters
        assert len(u["password_hash"]) == 64
        # Salt hex string is 32 characters (16 bytes)
        assert len(u["salt"]) == 32
        assert u["username"] is not None

def test_no_sensitive_credentials_in_api_responses(client):
    """Verify passwords, password hashes, and salts are NEVER returned in API responses."""
    # 1. Login response
    login_res = client.post("/api/auth/login", json={"username": "stu1015", "password": "campus123"})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "password" not in login_data
    assert "password_hash" not in login_data
    assert "salt" not in login_data
    token = login_data["token"]

    # 2. Session validation (/api/auth/me) response
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_str = me_res.text.lower()
    assert "password_hash" not in me_str
    assert "salt" not in me_str

    # 3. Change password response
    change_res = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {token}"}, json={
        "current_password": "campus123",
        "new_password": "Safe#Pass2026",
        "confirm_password": "Safe#Pass2026"
    })
    assert change_res.status_code == 200
    change_str = change_res.text.lower()
    assert "password_hash" not in change_str
    assert "salt" not in change_str

    # Restore password for STU1015
    auth_db.reset_password("stu1015", "campus123")

def test_sessions_table_records_all_required_columns(client):
    """Verify session table contains student_id, username, student_name, timestamps, status, IP, user_agent."""
    import sqlite3
    login_res = client.post(
        "/api/auth/login",
        json={"username": "stu1002", "password": "campus123"},
        headers={"User-Agent": "TestClient-Browser/1.0"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["token"]

    # Verify session in SQLite
    conn = sqlite3.connect(auth_db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (token,))
    sess = cursor.fetchone()
    assert sess is not None
    assert sess["student_id"] == "STU1002"
    assert sess["username"] == "stu1002"
    assert sess["student_name"] == "Surya Kumar"
    assert sess["login_timestamp"] is not None
    assert sess["logout_timestamp"] is None
    assert sess["status"] == "active"
    assert "TestClient" in (sess["user_agent"] or "")

    # Logout and verify update in SQLite
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200

    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (token,))
    sess_after = cursor.fetchone()
    assert sess_after["status"] == "logged_out"
    assert sess_after["logout_timestamp"] is not None
    assert sess_after["logout_timestamp"] >= sess_after["login_timestamp"]

def test_frontend_ui_has_no_login_history_elements():
    """Verify Login History page and sidebar entry are completely absent from frontend source."""
    # 1. LoginHistory.jsx must not exist
    assert not os.path.exists("frontend/src/pages/LoginHistory.jsx")

    # 2. Sidebar must not have 'Login History' or History icon
    with open("frontend/src/components/Sidebar.jsx", "r", encoding="utf-8") as f:
        sidebar_code = f.read()
    assert "Login History" not in sidebar_code
    assert "id: 'history'" not in sidebar_code

    # 3. App.jsx must not import or render LoginHistory
    with open("frontend/src/App.jsx", "r", encoding="utf-8") as f:
        app_code = f.read()
    assert "LoginHistory" not in app_code
    assert "activePage === 'history'" not in app_code

def test_real_database_untouched_and_isolated():
    """Verify that automated tests run strictly against test_auth.db and never modify data/auth.db."""
    import sqlite3
    assert auth_db.db_path != os.path.join("data", "auth.db")
    assert "test_auth.db" in auth_db.db_path

    # Verify real database state remains exactly preserved
    conn = sqlite3.connect("data/auth.db")
    cursor = conn.cursor()
    total_sessions = cursor.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    active_sessions = cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'active'").fetchone()[0]
    logged_out_sessions = cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'logged_out'").fetchone()[0]
    testclient_sessions = cursor.execute("SELECT COUNT(*) FROM sessions WHERE user_agent LIKE '%TestClient%'").fetchone()[0]
    assert total_sessions >= 260, f"Expected >= 260 sessions in data/auth.db, found {total_sessions}"
    assert testclient_sessions == 241, f"Expected exactly 241 legacy TestClient sessions in data/auth.db, found {testclient_sessions}"
    assert active_sessions <= 20, f"Expected <= 20 active sessions in data/auth.db, found {active_sessions}"
    student_users = cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0]
    assert student_users == 120, f"Expected 120 student users in data/auth.db, found {student_users}"
    total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert total_users in (120, 121), f"Expected 120 or 121 users in data/auth.db, found {total_users}"

def test_failed_login_protection_rate_limiting(client):
    """Test repeated failed login attempts trigger 429 Too Many Requests lockout."""
    from backend.main import _failed_login_attempts
    _failed_login_attempts.pop("stu1020", None)

    # 5 consecutive failed attempts
    for i in range(5):
        res = client.post("/api/auth/login", json={"username": "stu1020", "password": f"wrong_{i}"})
        assert res.status_code == 401, f"Attempt {i+1} should return 401"

    # 6th attempt must be blocked by rate limiter with 429
    blocked_res = client.post("/api/auth/login", json={"username": "stu1020", "password": "campus123"})
    assert blocked_res.status_code == 429
    assert "too many failed login attempts" in blocked_res.json()["detail"].lower()

    # Verify other student account is not blocked
    other_res = client.post("/api/auth/login", json={"username": "stu1025", "password": "campus123"})
    assert other_res.status_code == 200

    # Clean up lockout state
    _failed_login_attempts.pop("stu1020", None)

def test_change_password_revokes_other_active_sessions(client):
    """Test changing password revokes other active sessions while preserving current session."""
    import sqlite3
    import secrets
    from src.auth_db import DEFAULT_DEMO_PASSWORD

    auth_db.reset_password("stu1052", DEFAULT_DEMO_PASSWORD)

    # 1. Login to obtain current session token (Session B)
    login_b = client.post("/api/auth/login", json={"username": "stu1052", "password": DEFAULT_DEMO_PASSWORD})
    assert login_b.status_code == 200
    token_b = login_b.json()["token"]

    # 2. Simulate an active second device session (Session A) directly in SQLite
    conn = sqlite3.connect(auth_db.db_path)
    cursor = conn.cursor()
    token_a = f"device_a_{secrets.token_hex(12)}"
    cursor.execute("""
        INSERT INTO sessions (session_id, student_id, username, student_name, login_timestamp, logout_timestamp, status)
        VALUES (?, 'STU1052', 'stu1052', 'Rhea Chatterjee', '2026-10-09T08:00:00Z', NULL, 'active')
    """, (token_a,))
    conn.commit()

    # Verify Session A is active
    res_a_before = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a_before.status_code == 200

    # 3. Change password using current session (Session B)
    change_res = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {token_b}"}, json={
        "current_password": DEFAULT_DEMO_PASSWORD,
        "new_password": "NewRevoke#Pass2026",
        "confirm_password": "NewRevoke#Pass2026"
    })
    assert change_res.status_code == 200

    # 4. Session B (current session) must still be valid
    res_b_after = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b_after.status_code == 200

    # 5. Session A (other device session) must now be revoked (401)
    res_a_after = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a_after.status_code == 401
    assert "logged out" in res_a_after.json()["detail"].lower()

    # Reset password back to default
    auth_db.reset_password("stu1052", DEFAULT_DEMO_PASSWORD)




