"""
auth_db.py
Persistent SQLite storage for student user credentials, login sessions, and login history.
Stored in data/auth.db. Never stores plain-text passwords.
"""

import os
import sqlite3
import hashlib
import secrets
import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd

DEFAULT_DB_PATH = os.path.join("data", "auth.db")
DEFAULT_DEMO_PASSWORD = "campus123"
SESSION_EXPIRY_SECONDS = 86400  # 24 hours standard session lifetime

def get_db_path() -> str:
    """Returns the configured database path from AUTH_DB_PATH environment variable or default."""
    return os.environ.get("AUTH_DB_PATH", DEFAULT_DB_PATH)

def _get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    target_path = db_path or get_db_path()
    dirname = os.path.dirname(target_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str, salt: str) -> str:
    """Derives a secure SHA-256 hash using PBKDF2 with a unique salt."""
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100000
    )
    return key.hex()

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """Verifies a plain-text password against the stored PBKDF2 hash and salt."""
    computed_hash = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)

def validate_password_complexity(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that a password satisfies all required security conditions:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character (@, #, $, !, etc.)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[@#$%!^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password):
        return False, "Password must contain at least one special character (e.g. @, #, $, !)."
    return True, None

class AuthDatabase:
    def __init__(self, db_path: Optional[str] = None, students_csv_path: str = os.path.join("data", "students.csv")):
        self.db_path = db_path or get_db_path()
        self.students_csv_path = students_csv_path
        self._initialize_schema()
        self._seed_demo_users()

    def _initialize_schema(self) -> None:
        """Creates the SQLite tables for users and persistent login sessions."""
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table (hashed credentials with username)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    student_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    student_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Schema migration: Ensure 'username' and 'role' columns exist
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            if "username" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
            if "role" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")

            # Ensure all existing rows have lowercase student_id as default username and student role
            cursor.execute("UPDATE users SET username = LOWER(student_id) WHERE username IS NULL OR username = ''")
            cursor.execute("UPDATE users SET role = 'student' WHERE role IS NULL OR role = ''")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username)")

            # Sessions table (unique session ID, student_id, username, student_name, login & logout timestamps, status)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    username TEXT,
                    student_name TEXT,
                    login_timestamp TEXT NOT NULL,
                    logout_timestamp TEXT,
                    status TEXT NOT NULL,
                    user_agent TEXT,
                    ip_address TEXT,
                    FOREIGN KEY(student_id) REFERENCES users(student_id)
                )
            """)

            # Schema migration: Ensure student_name & username columns exist
            cursor.execute("PRAGMA table_info(sessions)")
            sess_cols = [col[1] for col in cursor.fetchall()]
            if "student_name" not in sess_cols:
                cursor.execute("ALTER TABLE sessions ADD COLUMN student_name TEXT")
            if "username" not in sess_cols:
                cursor.execute("ALTER TABLE sessions ADD COLUMN username TEXT")

            cursor.execute("""
                UPDATE sessions 
                SET student_name = (SELECT student_name FROM users WHERE users.student_id = sessions.student_id)
                WHERE student_name IS NULL OR student_name = ''
            """)
            cursor.execute("""
                UPDATE sessions 
                SET username = (SELECT username FROM users WHERE users.student_id = sessions.student_id)
                WHERE username IS NULL OR username = ''
            """)

            # Index for fast student session history lookup
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_student_id 
                ON sessions(student_id, login_timestamp DESC)
            """)

            # Persistent Academic & Attendance Overrides tables (SQLite)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS academic_updates (
                    student_id TEXT NOT NULL,
                    subject_name TEXT NOT NULL,
                    marks REAL NOT NULL,
                    updated_at TEXT NOT NULL,
                    updated_by TEXT DEFAULT 'faculty',
                    PRIMARY KEY(student_id, subject_name)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance_updates (
                    student_id TEXT NOT NULL,
                    subject_name TEXT NOT NULL,
                    classes_attended INTEGER NOT NULL,
                    total_classes INTEGER NOT NULL,
                    attendance_percentage REAL NOT NULL,
                    updated_at TEXT NOT NULL,
                    updated_by TEXT DEFAULT 'faculty',
                    PRIMARY KEY(student_id, subject_name)
                )
            """)

            # Persistent Recommendation Completions table (SQLite)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendation_completions (
                    student_id TEXT NOT NULL,
                    recommendation_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    completed_at TEXT,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(student_id, recommendation_id)
                )
            """)

            # Persistent Custom Improvement Plans table (SQLite)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_improvement_plans (
                    plan_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'Medium',
                    target_date TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rec_completions_student
                ON recommendation_completions(student_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_custom_plans_student
                ON custom_improvement_plans(student_id, created_at DESC)
            """)
            conn.commit()

        # Reconcile existing historical session statuses
        self._reconcile_existing_sessions()

    def _seed_demo_users(self) -> None:
        """Seeds demo user records for all students in students.csv if not already present."""
        if not os.path.exists(self.students_csv_path):
            return

        df_students = pd.read_csv(self.students_csv_path)
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            now_iso = datetime.now(timezone.utc).isoformat()

            for _, row in df_students.iterrows():
                s_id = str(row["student_id"]).strip()
                s_name = str(row["student_name"]).strip()
                uname = s_id.lower()

                cursor.execute("SELECT student_id, username FROM users WHERE student_id = ?", (s_id,))
                existing = cursor.fetchone()
                if existing is None:
                    salt = secrets.token_hex(16)
                    # All demo accounts are seeded with PBKDF2 hash of demo password
                    pwd_hash = hash_password(DEFAULT_DEMO_PASSWORD, salt)
                    cursor.execute("""
                        INSERT INTO users (student_id, username, student_name, password_hash, salt, created_at, role)
                        VALUES (?, ?, ?, ?, ?, ?, 'student')
                    """, (s_id, uname, s_name, pwd_hash, salt, now_iso))
                else:
                    if not existing["username"]:
                        cursor.execute("UPDATE users SET username = ? WHERE student_id = ?", (uname, s_id))

            # Seed demo faculty account if not present
            cursor.execute("SELECT student_id FROM users WHERE username = 'faculty' OR student_id = 'FAC001'")
            existing_faculty = cursor.fetchone()
            if existing_faculty is None:
                fac_salt = secrets.token_hex(16)
                fac_pwd_hash = hash_password(DEFAULT_DEMO_PASSWORD, fac_salt)
                cursor.execute("""
                    INSERT INTO users (student_id, username, student_name, password_hash, salt, created_at, role)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("FAC001", "faculty", "Prof. Rajesh Sharma", fac_pwd_hash, fac_salt, now_iso, "faculty"))

            conn.commit()

    def authenticate_user(self, username_or_id: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Validates student or faculty credentials against stored PBKDF2 hash.
        Matches by username or student_id (case-insensitive).
        Returns user info dictionary if authenticated, or None if invalid.
        """
        clean_identifier = username_or_id.strip()
        if not clean_identifier or not password:
            return None

        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(student_id) = LOWER(?)", 
                (clean_identifier, clean_identifier)
            )
            user = cursor.fetchone()
            if not user:
                return None

            # Verify password securely using PBKDF2 with stored salt
            is_valid = verify_password(password, user["salt"], user["password_hash"])
            if is_valid:
                return {
                    "student_id": user["student_id"],
                    "username": user["username"] if "username" in user.keys() and user["username"] else user["student_id"].lower(),
                    "student_name": user["student_name"],
                    "created_at": user["created_at"],
                    "role": user["role"] if "role" in user.keys() and user["role"] else "student"
                }
            return None

    def create_user(
        self, 
        student_id: str, 
        username: str, 
        password: str, 
        student_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates or updates a user with a unique salt and PBKDF2 hashed password."""
        clean_id = student_id.strip().upper()
        clean_uname = username.strip().lower()
        salt = secrets.token_hex(16)
        pwd_hash = hash_password(password, salt)
        now_iso = datetime.now(timezone.utc).isoformat()
        name = student_name or clean_id

        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (student_id, username, student_name, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id) DO UPDATE SET
                    username = excluded.username,
                    student_name = excluded.student_name,
                    password_hash = excluded.password_hash,
                    salt = excluded.salt
            """, (clean_id, clean_uname, name, pwd_hash, salt, now_iso))
            conn.commit()

        return {
            "student_id": clean_id,
            "username": clean_uname,
            "student_name": name,
            "created_at": now_iso
        }

    def reset_password(self, username_or_id: str, new_password: str) -> bool:
        """Updates the password for an existing user account."""
        clean_identifier = username_or_id.strip()
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT student_id FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(student_id) = LOWER(?)",
                (clean_identifier, clean_identifier)
            )
            row = cursor.fetchone()
            if not row:
                return False
            student_id = row["student_id"]
            salt = secrets.token_hex(16)
            pwd_hash = hash_password(new_password, salt)
            cursor.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE student_id = ?",
                (pwd_hash, salt, student_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def change_password(
        self, 
        student_id: str, 
        current_password: str, 
        new_password: str,
        current_session_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Securely updates a student's password after verifying the current password
        and validating the new password's complexity.
        Revokes other active sessions for this student account.
        """
        clean_id = student_id.strip().upper()
        if not current_password:
            return False, "Current password is required."
        if not new_password:
            return False, "New password is required."

        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash, salt FROM users WHERE student_id = ?", (clean_id,))
            user = cursor.fetchone()
            if not user:
                return False, "User account not found."

            # Verify current password against stored hash and salt
            if not verify_password(current_password, user["salt"], user["password_hash"]):
                return False, "Incorrect current password."

            # Validate complexity conditions on new password
            is_valid, err_msg = validate_password_complexity(new_password)
            if not is_valid:
                return False, err_msg or "Password does not meet complexity requirements."

            # Derive fresh unique cryptographic salt and PBKDF2 hash
            new_salt = secrets.token_hex(16)
            new_hash = hash_password(new_password, new_salt)

            cursor.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE student_id = ?",
                (new_hash, new_salt, clean_id)
            )

            # Revoke other active sessions for this student
            now_iso = datetime.now(timezone.utc).isoformat()
            if current_session_id:
                cursor.execute("""
                    UPDATE sessions 
                    SET logout_timestamp = ?, status = 'logged_out' 
                    WHERE student_id = ? AND status = 'active' AND session_id != ?
                """, (now_iso, clean_id, current_session_id))
            else:
                cursor.execute("""
                    UPDATE sessions 
                    SET logout_timestamp = ?, status = 'logged_out' 
                    WHERE student_id = ? AND status = 'active'
                """, (now_iso, clean_id))

            conn.commit()
            return True, "Password updated successfully."

    def _reconcile_existing_sessions(self) -> None:
        """
        Reconciles historical session records in SQLite:
        - For any student who has multiple 'active' sessions, marks older superseded
          sessions as 'logged_out' with an estimated logout timestamp.
        - Marks any active sessions older than SESSION_EXPIRY_SECONDS as 'logged_out'.
        - Preserves all rows permanently in SQLite without deleting any records.
        """
        now = datetime.now(timezone.utc)
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()

            # Find students with multiple active sessions
            cursor.execute("""
                SELECT student_id, COUNT(*) as cnt 
                FROM sessions 
                WHERE status = 'active' 
                GROUP BY student_id 
                HAVING cnt > 1
            """)
            multi_active = cursor.fetchall()
            for row in multi_active:
                s_id = row["student_id"]
                cursor.execute("""
                    SELECT session_id, login_timestamp 
                    FROM sessions 
                    WHERE student_id = ? AND status = 'active'
                    ORDER BY login_timestamp DESC
                """, (s_id,))
                sessions_list = cursor.fetchall()
                # Index 0 is the most recent (keep active if not expired)
                # All other older active sessions are marked as logged_out
                for i in range(1, len(sessions_list)):
                    older_row = sessions_list[i]
                    newer_row = sessions_list[i - 1]
                    cursor.execute("""
                        UPDATE sessions 
                        SET logout_timestamp = ?, status = 'logged_out'
                        WHERE session_id = ?
                    """, (newer_row["login_timestamp"], older_row["session_id"]))

            # Expire any active sessions older than SESSION_EXPIRY_SECONDS
            cursor.execute("SELECT session_id, login_timestamp FROM sessions WHERE status = 'active'")
            for row in cursor.fetchall():
                try:
                    t_in = datetime.fromisoformat(row["login_timestamp"])
                    if (now - t_in).total_seconds() > SESSION_EXPIRY_SECONDS:
                        logout_time = (t_in + timedelta(seconds=SESSION_EXPIRY_SECONDS)).isoformat()
                        cursor.execute("""
                            UPDATE sessions 
                            SET logout_timestamp = ?, status = 'logged_out'
                            WHERE session_id = ?
                        """, (logout_time, row["session_id"]))
                except Exception:
                    pass

            conn.commit()

    def create_session(self, student_id: str, user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates and stores a new active login session in SQLite.
        Inserts one new permanent row for every login.
        Closes any previously unclosed active session for this student.
        """
        clean_id = student_id.strip().upper()
        now_dt = datetime.now(timezone.utc)
        login_timestamp = now_dt.isoformat()
        session_id = secrets.token_hex(24)
        status = "active"

        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()

            # 1. Close any prior active sessions for this student so they do not linger as active
            cursor.execute("""
                UPDATE sessions 
                SET logout_timestamp = ?, status = 'logged_out'
                WHERE student_id = ? AND status = 'active'
            """, (login_timestamp, clean_id))

            # 2. Get student_name, username, and role from users table
            cursor.execute("SELECT student_name, username, role FROM users WHERE student_id = ?", (clean_id,))
            user_row = cursor.fetchone()
            student_name = user_row["student_name"] if user_row else clean_id
            username = (user_row["username"] if user_row and user_row["username"] else clean_id.lower())
            user_role = (user_row["role"] if user_row and "role" in user_row.keys() and user_row["role"] else "student")

            # 3. Insert one brand new session row
            cursor.execute("""
                INSERT INTO sessions (
                    session_id, student_id, username, student_name, login_timestamp, logout_timestamp, 
                    status, user_agent, ip_address
                )
                VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?)
            """, (session_id, clean_id, username, student_name, login_timestamp, status, user_agent, ip_address))
            conn.commit()

        return {
            "session_id": session_id,
            "student_id": clean_id,
            "username": username,
            "student_name": student_name,
            "role": user_role,
            "login_timestamp": login_timestamp,
            "status": status
        }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves session details by session_id."""
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Validates that a session exists, is active, and has not expired.
        If expired, automatically marks it logged_out.
        Attaches role from users table.
        """
        session = self.get_session(session_id)
        if not session or session["status"] != "active":
            return None

        # Check if session has exceeded session lifetime
        try:
            t_in = datetime.fromisoformat(session["login_timestamp"])
            now = datetime.now(timezone.utc)
            if (now - t_in).total_seconds() > SESSION_EXPIRY_SECONDS:
                self.logout_session(session_id)
                return None
        except Exception:
            pass

        # Attach role from users table
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, username, student_name FROM users WHERE student_id = ?", (session["student_id"],))
            u = cursor.fetchone()
            session["role"] = (u["role"] if u and "role" in u.keys() and u["role"] else "student")
            if u and u["username"]:
                session["username"] = u["username"]
            if u and u["student_name"]:
                session["student_name"] = u["student_name"]

        return session

    def logout_session(self, session_id: str) -> bool:
        """Marks an active session as logged out with logout timestamp in SQLite."""
        logout_timestamp = datetime.now(timezone.utc).isoformat()
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions 
                SET logout_timestamp = ?, status = 'logged_out'
                WHERE session_id = ? AND status = 'active'
            """, (logout_timestamp, session_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_student_login_history(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves login history for a specific student, sorted from newest to oldest.
        Ensures students only see their own login history.
        """
        clean_id = student_id.strip().upper()
        # Reconcile expired sessions
        self._reconcile_existing_sessions()

        history = []
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, student_id, username, student_name, login_timestamp, 
                       logout_timestamp, status, user_agent, ip_address
                FROM sessions
                WHERE student_id = ?
                ORDER BY login_timestamp DESC
            """, (clean_id,))
            rows = cursor.fetchall()
            for r in rows:
                row_dict = dict(r)
                # Fallback student_name if null
                if not row_dict.get("student_name"):
                    cursor.execute("SELECT student_name FROM users WHERE student_id = ?", (clean_id,))
                    u = cursor.fetchone()
                    row_dict["student_name"] = u["student_name"] if u else clean_id

                # Compute duration in human-readable format if logged out
                duration_str = None
                if row_dict["logout_timestamp"]:
                    try:
                        t_in = datetime.fromisoformat(row_dict["login_timestamp"])
                        t_out = datetime.fromisoformat(row_dict["logout_timestamp"])
                        diff_sec = max(0, int((t_out - t_in).total_seconds()))
                        if diff_sec < 60:
                            duration_str = f"{diff_sec}s"
                        elif diff_sec < 3600:
                            duration_str = f"{diff_sec // 60}m {diff_sec % 60}s"
                        else:
                            duration_str = f"{diff_sec // 3600}h {(diff_sec % 3600) // 60}m"
                    except Exception:
                        pass
                row_dict["duration"] = duration_str or ("Active Session" if row_dict["status"] == "active" else "Concluded")
                history.append(row_dict)
        return history

    def get_session_stats(self) -> Dict[str, Any]:
        """Returns overall session counts from SQLite."""
        self._reconcile_existing_sessions()
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            total = cursor.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            active = cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'active'").fetchone()[0]
            logged_out = cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'logged_out'").fetchone()[0]
            return {
                "total_sessions": total,
                "active_sessions": active,
                "logged_out_sessions": logged_out
            }

    def save_academic_update(self, student_id: str, subject_name: str, marks: float, updated_by: str = "faculty") -> None:
        """Persists a subject mark update for a student in SQLite academic_updates table."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO academic_updates (student_id, subject_name, marks, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(student_id, subject_name) DO UPDATE SET
                    marks = excluded.marks,
                    updated_at = excluded.updated_at,
                    updated_by = excluded.updated_by
            """, (student_id.strip().upper(), subject_name.strip(), float(marks), now_iso, updated_by))
            conn.commit()

    def save_attendance_update(self, student_id: str, subject_name: str, attended: int, total: int, updated_by: str = "faculty") -> None:
        """Persists course attendance numbers and percentage for a student in SQLite attendance_updates table."""
        now_iso = datetime.now(timezone.utc).isoformat()
        pct = round((attended / total) * 100.0, 2)
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attendance_updates (student_id, subject_name, classes_attended, total_classes, attendance_percentage, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, subject_name) DO UPDATE SET
                    classes_attended = excluded.classes_attended,
                    total_classes = excluded.total_classes,
                    attendance_percentage = excluded.attendance_percentage,
                    updated_at = excluded.updated_at,
                    updated_by = excluded.updated_by
            """, (student_id.strip().upper(), subject_name.strip(), int(attended), int(total), pct, now_iso, updated_by))
            conn.commit()

    def get_academic_updates(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves persisted academic marks overrides from SQLite, optionally filtered by student_id."""
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            if student_id:
                cursor.execute(
                    "SELECT student_id, subject_name, marks, updated_at, updated_by FROM academic_updates WHERE student_id = ?",
                    (student_id.strip().upper(),)
                )
            else:
                cursor.execute("SELECT student_id, subject_name, marks, updated_at, updated_by FROM academic_updates")
            return [dict(r) for r in cursor.fetchall()]

    def get_attendance_updates(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves persisted attendance overrides from SQLite, optionally filtered by student_id."""
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            if student_id:
                cursor.execute(
                    "SELECT student_id, subject_name, classes_attended, total_classes, attendance_percentage, updated_at, updated_by FROM attendance_updates WHERE student_id = ?",
                    (student_id.strip().upper(),)
                )
            else:
                cursor.execute("SELECT student_id, subject_name, classes_attended, total_classes, attendance_percentage, updated_at, updated_by FROM attendance_updates")
            return [dict(r) for r in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Improvement Plan & Custom Tasks Management
    # -------------------------------------------------------------------------
    def set_recommendation_status(self, student_id: str, recommendation_id: str, status: str) -> Dict[str, Any]:
        """Saves or updates the completion status for a system recommendation."""
        clean_id = student_id.strip().upper()
        clean_rec = recommendation_id.strip()
        status_norm = 'completed' if status.lower() == 'completed' else 'pending'
        now_iso = datetime.now(timezone.utc).isoformat()
        completed_at = now_iso if status_norm == 'completed' else None

        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO recommendation_completions (student_id, recommendation_id, status, completed_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(student_id, recommendation_id) DO UPDATE SET
                    status = excluded.status,
                    completed_at = excluded.completed_at,
                    updated_at = excluded.updated_at
            """, (clean_id, clean_rec, status_norm, completed_at, now_iso))
            conn.commit()

        return {
            "student_id": clean_id,
            "recommendation_id": clean_rec,
            "status": status_norm,
            "is_completed": status_norm == "completed",
            "completed_at": completed_at,
            "updated_at": now_iso
        }

    def get_recommendation_completions(self, student_id: str) -> Dict[str, Dict[str, Any]]:
        """Retrieves all recommendation completion statuses for a student."""
        clean_id = student_id.strip().upper()
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT recommendation_id, status, completed_at, updated_at
                FROM recommendation_completions
                WHERE student_id = ?
            """, (clean_id,))
            rows = cursor.fetchall()
            return {
                r["recommendation_id"]: {
                    "status": r["status"],
                    "is_completed": r["status"] == "completed",
                    "completed_at": r["completed_at"],
                    "updated_at": r["updated_at"]
                }
                for r in rows
            }

    def create_custom_plan(
        self,
        student_id: str,
        title: str,
        description: Optional[str] = None,
        category: str = "Academic",
        priority: str = "Medium",
        target_date: Optional[str] = None,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Creates and stores a student-created custom improvement plan."""
        clean_id = student_id.strip().upper()
        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        status_norm = 'completed' if status.lower() == 'completed' else 'pending'
        completed_at = now_iso if status_norm == 'completed' else None

        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO custom_improvement_plans (
                    plan_id, student_id, title, description, category,
                    priority, target_date, status, created_at, updated_at, completed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan_id, clean_id, title.strip(),
                description.strip() if description else None,
                category.strip() if category else "Other",
                priority.capitalize() if priority else "Medium",
                target_date.strip() if target_date else None,
                status_norm, now_iso, now_iso, completed_at
            ))
            conn.commit()

        return self.get_custom_plan(clean_id, plan_id)

    def get_custom_plans(self, student_id: str) -> List[Dict[str, Any]]:
        """Retrieves all custom plans created by a specific student."""
        clean_id = student_id.strip().upper()
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT plan_id, student_id, title, description, category,
                       priority, target_date, status, created_at, updated_at, completed_at
                FROM custom_improvement_plans
                WHERE student_id = ?
                ORDER BY created_at DESC
            """, (clean_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_custom_plan(self, student_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single custom plan ensuring student ownership."""
        clean_id = student_id.strip().upper()
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT plan_id, student_id, title, description, category,
                       priority, target_date, status, created_at, updated_at, completed_at
                FROM custom_improvement_plans
                WHERE plan_id = ? AND student_id = ?
            """, (plan_id.strip(), clean_id))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_custom_plan(
        self,
        student_id: str,
        plan_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Updates a custom plan record for an authorized student."""
        clean_id = student_id.strip().upper()
        clean_plan_id = plan_id.strip()

        existing = self.get_custom_plan(clean_id, clean_plan_id)
        if not existing:
            return None

        now_iso = datetime.now(timezone.utc).isoformat()
        title = updates.get("title", existing["title"])
        description = updates.get("description", existing["description"])
        category = updates.get("category", existing["category"])
        priority = updates.get("priority", existing["priority"])
        target_date = updates.get("target_date", existing["target_date"])
        
        status = existing["status"]
        completed_at = existing["completed_at"]
        if "status" in updates:
            new_status = 'completed' if updates["status"].lower() == 'completed' else 'pending'
            if new_status != status:
                status = new_status
                completed_at = now_iso if status == 'completed' else None

        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE custom_improvement_plans
                SET title = ?, description = ?, category = ?, priority = ?,
                    target_date = ?, status = ?, completed_at = ?, updated_at = ?
                WHERE plan_id = ? AND student_id = ?
            """, (
                title.strip() if title else existing["title"],
                description.strip() if description else None,
                category.strip() if category else existing["category"],
                priority.capitalize() if priority else existing["priority"],
                target_date.strip() if target_date else None,
                status, completed_at, now_iso,
                clean_plan_id, clean_id
            ))
            conn.commit()

        return self.get_custom_plan(clean_id, clean_plan_id)

    def delete_custom_plan(self, student_id: str, plan_id: str) -> bool:
        """Deletes a custom plan record verifying student ownership."""
        clean_id = student_id.strip().upper()
        with _get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM custom_improvement_plans
                WHERE plan_id = ? AND student_id = ?
            """, (plan_id.strip(), clean_id))
            conn.commit()
            return cursor.rowcount > 0
