"""
main.py
FastAPI Backend Application for Smart Campus Analytics.
Includes persistent SQLite login sessions, authentication, student data authorization,
and RESTful analytics endpoints.
"""

import os
import sys
import time
from collections import defaultdict
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Header, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.service import AnalyticsService
from src.auth_db import AuthDatabase, DEFAULT_DEMO_PASSWORD

app = FastAPI(
    title="Smart Campus Analytics API",
    description="Backend REST API providing student analytics, persistent sessions, and login history.",
    version="2.0.0"
)

# CORS configuration for frontend consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
service = AnalyticsService()
service.initialize()
auth_db = AuthDatabase()

def get_auth_db() -> AuthDatabase:
    """Returns the current AuthDatabase instance, syncing with AUTH_DB_PATH if configured."""
    global auth_db
    expected_path = os.environ.get("AUTH_DB_PATH", os.path.join("data", "auth.db"))
    if auth_db is None or auth_db.db_path != expected_path:
        auth_db = AuthDatabase(db_path=expected_path)
    return auth_db

# -----------------------------------------------------------------------------
# Protection Against Repeated Failed Login Attempts
# -----------------------------------------------------------------------------
MAX_FAILED_LOGIN_ATTEMPTS = 5
FAILED_LOGIN_WINDOW_SECONDS = 300  # 5 minutes window

_failed_login_attempts: Dict[str, List[float]] = defaultdict(list)

def check_failed_login_attempts(identifier: str) -> None:
    """Raises HTTP 429 if consecutive failed logins for identifier exceed threshold."""
    key = identifier.strip().lower()
    now = time.time()
    recent = [t for t in _failed_login_attempts[key] if (now - t) < FAILED_LOGIN_WINDOW_SECONDS]
    _failed_login_attempts[key] = recent
    if len(recent) >= MAX_FAILED_LOGIN_ATTEMPTS:
        lockout_remaining = int(FAILED_LOGIN_WINDOW_SECONDS - (now - recent[0]))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts for '{identifier}'. Account temporarily locked. Please try again in {max(1, lockout_remaining)} seconds."
        )

def record_failed_login(identifier: str) -> None:
    """Records a failed login attempt."""
    key = identifier.strip().lower()
    _failed_login_attempts[key].append(time.time())

def record_successful_login(identifier: str) -> None:
    """Clears failed attempts counter upon successful authentication."""
    key = identifier.strip().lower()
    _failed_login_attempts.pop(key, None)

# -----------------------------------------------------------------------------
# Pydantic Request Models
# -----------------------------------------------------------------------------
class LoginRequest(BaseModel):
    username: Optional[str] = None
    student_id: Optional[str] = None
    password: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: Optional[str] = None

class SubjectMarkUpdate(BaseModel):
    subject_name: str
    marks: float = Field(..., ge=0.0, le=100.0)

class SubjectAttendanceUpdate(BaseModel):
    subject_name: str
    classes_attended: int = Field(..., ge=0)
    total_classes: int = Field(..., gt=0)

class FacultyUpdateRequest(BaseModel):
    academic_updates: Optional[List[SubjectMarkUpdate]] = None
    attendance_updates: Optional[List[SubjectAttendanceUpdate]] = None

class RecommendationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(completed|pending)$")

class CustomPlanCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field("Academic", pattern="^(Academic|Attendance|Coding|Aptitude|Communication|Placement|Skills|Other)$")
    priority: str = Field("Medium", pattern="^(Low|Medium|High)$")
    target_date: Optional[str] = None

class CustomPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, pattern="^(Academic|Attendance|Coding|Aptitude|Communication|Placement|Skills|Other)$")
    priority: Optional[str] = Field(None, pattern="^(Low|Medium|High)$")
    target_date: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(completed|pending)$")

# -----------------------------------------------------------------------------
# Authentication Dependency
# -----------------------------------------------------------------------------
def get_current_session(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Extracts and validates session token from Authorization or X-Session-ID header.
    Returns the active session dict or raises 401 Unauthorized.
    """
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        elif len(parts) == 1:
            token = parts[0]
    elif x_session_id:
        token = x_session_id

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid session ID."
        )

    session = get_auth_db().validate_session(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid, expired, or logged out. Please log in again."
        )

    return session

# -----------------------------------------------------------------------------
# System & Health Endpoints
# -----------------------------------------------------------------------------
@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint reporting API, session storage, and analytics readiness."""
    return {
        "status": "healthy",
        "service": "Smart Campus Analytics API",
        "version": "2.0.0",
        "student_count": len(service.student_dossiers),
        "auth_database": f"SQLite ({get_auth_db().db_path})",
        "synthetic_notice": "Demonstration dataset with 120 fictional students"
    }

# -----------------------------------------------------------------------------
# Authentication Endpoints
# -----------------------------------------------------------------------------
@app.post("/api/auth/login")
def login(login_req: LoginRequest, request: Request) -> Dict[str, Any]:
    """
    Validates student credentials and creates a persistent session in SQLite.
    Accepts username (or student_id) and password.
    Never defaults to any specific student.
    """
    identifier = (login_req.username or login_req.student_id or "").strip()
    password = (login_req.password or "").strip()

    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is required."
        )
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required."
        )

    # Check protection against repeated failed attempts
    check_failed_login_attempts(identifier)

    user = get_auth_db().authenticate_user(identifier, password)
    if not user:
        record_failed_login(identifier)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Please check your credentials."
        )

    # Clear failed attempt counter on successful login
    record_successful_login(identifier)

    user_agent = request.headers.get("user-agent", "Unknown")
    client_ip = request.client.host if request.client else "127.0.0.1"

    session = get_auth_db().create_session(
        student_id=user["student_id"],
        user_agent=user_agent,
        ip_address=client_ip
    )

    # Fetch student profile for frontend convenience (if student)
    user_role = user.get("role", "student")
    profile = service.get_student_profile(user["student_id"], auth_db_instance=get_auth_db()) if user_role == "student" else None

    return {
        "token": session["session_id"],
        "session_id": session["session_id"],
        "student_id": user["student_id"],
        "username": user.get("username", user["student_id"].lower()),
        "student_name": user["student_name"],
        "role": user_role,
        "department": profile["personal_info"]["department"] if profile else ("Faculty Administration" if user_role == "faculty" else ""),
        "login_timestamp": session["login_timestamp"],
        "status": session["status"]
    }

@app.get("/api/auth/me")
def get_current_user_session(session: Dict[str, Any] = Depends(get_current_session)) -> Dict[str, Any]:
    """
    Restores and validates the active session on page refresh.
    Returns authenticated student profile or faculty profile and active session metadata.
    """
    user_role = session.get("role", "student")
    if user_role == "faculty":
        return {
            "session": {
                "session_id": session["session_id"],
                "login_timestamp": session["login_timestamp"],
                "status": session["status"],
                "role": "faculty"
            },
            "faculty": {
                "faculty_id": session["student_id"],
                "username": session.get("username", "faculty"),
                "name": session.get("student_name", "Prof. Rajesh Sharma"),
                "department": "Academic Faculty & Administration",
                "role": "faculty"
            },
            "user": {
                "student_id": session["student_id"],
                "username": session.get("username", "faculty"),
                "student_name": session.get("student_name", "Prof. Rajesh Sharma"),
                "role": "faculty"
            },
            "student": None,
            "role": "faculty"
        }

    student_id = session["student_id"]
    profile = service.get_student_profile(student_id, auth_db_instance=get_auth_db())
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record for ID '{student_id}' not found."
        )

    return {
        "session": {
            "session_id": session["session_id"],
            "login_timestamp": session["login_timestamp"],
            "status": session["status"],
            "role": "student"
        },
        "student": profile,
        "user": {
            "student_id": session["student_id"],
            "username": session.get("username", student_id.lower()),
            "student_name": session.get("student_name") or profile.get("personal_info", {}).get("student_name", ""),
            "role": "student"
        },
        "role": "student"
    }

@app.post("/api/auth/logout")
def logout(session: Dict[str, Any] = Depends(get_current_session)) -> Dict[str, Any]:
    """
    Invalidates the active session in SQLite and records logout timestamp.
    """
    success = get_auth_db().logout_session(session["session_id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to terminate session or session already ended."
        )

    return {
        "status": "logged_out",
        "message": "Session terminated successfully."
    }

@app.get("/api/auth/history")
def get_login_history(session: Dict[str, Any] = Depends(get_current_session)) -> List[Dict[str, Any]]:
    """
    Retrieves login history for ONLY the currently authenticated student.
    Strictly prevents exposing other students' session logs.
    """
    student_id = session["student_id"]
    return get_auth_db().get_student_login_history(student_id)

@app.post("/api/auth/change-password")
def change_password(
    req: ChangePasswordRequest,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """
    Securely updates the authenticated student's password in SQLite.
    Validates current password, password complexity, and confirmation match.
    """
    if req.confirm_password is not None and req.confirm_password != req.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match."
        )

    success, message = get_auth_db().change_password(
        student_id=session["student_id"],
        current_password=req.current_password,
        new_password=req.new_password,
        current_session_id=session.get("session_id")
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    return {
        "status": "success",
        "message": "Password updated successfully."
    }

# -----------------------------------------------------------------------------
# Protected Student Directory Endpoint (Requires Authentication)
# -----------------------------------------------------------------------------
@app.get("/api/students")
def get_students(
    search: Optional[str] = None,
    department: Optional[str] = None,
    risk: Optional[str] = None,
    session: Dict[str, Any] = Depends(get_current_session)
) -> List[Dict[str, Any]]:
    """
    Returns student directory for authenticated students only.
    Protected against unauthenticated public access.
    """
    students_list = []
    for s_id, d in service.student_dossiers.items():
        p = d["personal_info"]
        sc = d["success_score"]["overall_score"]
        acad_risk = d["risk_analysis"]["academic_risk"]["level"]
        place_risk = d["risk_analysis"]["placement_risk"]["level"]
        seg = d["segmentation"]["segment_name"]

        if search:
            q = search.lower()
            if q not in s_id.lower() and q not in p["student_name"].lower():
                continue
        if department and department != "All" and p["department"] != department:
            continue
        if risk and risk != "All":
            if risk == "High Risk" and acad_risk != "High" and place_risk != "High":
                continue
            elif risk == "Moderate Risk" and acad_risk != "Moderate" and place_risk != "Moderate":
                continue
            elif risk == "Low Risk" and (acad_risk != "Low" or place_risk != "Low"):
                continue

        students_list.append({
            "student_id": s_id,
            "student_name": p["student_name"],
            "department": p["department"],
            "academic_year": p["academic_year"],
            "semester": p["semester"],
            "email": p["email"],
            "success_score": sc,
            "academic_risk_level": acad_risk,
            "placement_risk_level": place_risk,
            "student_segment": seg
        })

    return students_list

# -----------------------------------------------------------------------------
# Protected Student-Specific Data Endpoints (Session Validated & Scope Checked)
# -----------------------------------------------------------------------------
@app.get("/api/students/{student_id}")
def get_student_profile(
    student_id: str,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """
    Retrieves full dossier for a specific student.
    Strictly verifies that authenticated user is faculty OR matches requested student_id.
    """
    clean_id = student_id.strip().upper()
    if session.get("role") != "faculty" and session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to access your own student profile."
        )

    dossier = service.get_student_profile(clean_id, auth_db_instance=get_auth_db())
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record with ID '{student_id}' not found."
        )
    return dossier

@app.get("/api/students/{student_id}/score")
def get_student_score(
    student_id: str,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """Returns detailed Student Success Score and breakdown for authenticated student or faculty."""
    clean_id = student_id.strip().upper()
    if session.get("role") != "faculty" and session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to access your own score."
        )

    dossier = service.get_student_profile(clean_id, auth_db_instance=get_auth_db())
    if not dossier:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found.")
    return dossier["success_score"]

@app.get("/api/students/{student_id}/risks")
def get_student_risks(
    student_id: str,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """Returns Academic and Placement risk diagnostics for authenticated student or faculty."""
    clean_id = student_id.strip().upper()
    if session.get("role") != "faculty" and session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to access your own risk analysis."
        )

    dossier = service.get_student_profile(clean_id, auth_db_instance=get_auth_db())
    if not dossier:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found.")
    return dossier["risk_analysis"]

@app.get("/api/students/{student_id}/recommendations")
def get_student_recommendations(
    student_id: str,
    session: Dict[str, Any] = Depends(get_current_session)
) -> List[Dict[str, Any]]:
    """Returns personalized actionable recommendations for authenticated student or faculty."""
    clean_id = student_id.strip().upper()
    if session.get("role") != "faculty" and session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to access your own recommendations."
        )

    dossier = service.get_student_profile(clean_id, auth_db_instance=get_auth_db())
    if not dossier:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found.")
    return dossier["recommendations"]

# -----------------------------------------------------------------------------
# Improvement Plan & Student Custom Tasks Endpoints (Student-Protected)
# -----------------------------------------------------------------------------
@app.get("/api/students/{student_id}/improvement-plan")
def get_student_improvement_plan(
    student_id: str,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """
    Returns consolidated Improvement Plan for the authenticated student:
    - System-generated recommendations with persisted completion statuses
    - Student-created custom tasks
    - Aggregated progress and completion statistics
    Enforces student-level isolation; students only see their own plan.
    """
    clean_id = student_id.strip().upper()
    if session.get("role") != "student" or session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to access your own improvement plan."
        )

    plan_data = service.get_student_improvement_plan(clean_id, auth_db_instance=get_auth_db())
    if not plan_data:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found.")
    return plan_data

@app.post("/api/students/{student_id}/recommendations/{recommendation_id}/status")
def update_recommendation_status(
    student_id: str,
    recommendation_id: str,
    req: RecommendationStatusUpdate,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """
    Persistently toggles or sets completion status for a system recommendation.
    Stored permanently in SQLite per student.
    """
    clean_id = student_id.strip().upper()
    if session.get("role") != "student" or session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to update your own recommendations."
        )

    res = get_auth_db().set_recommendation_status(
        student_id=clean_id,
        recommendation_id=recommendation_id,
        status=req.status
    )
    plan_data = service.get_student_improvement_plan(clean_id, auth_db_instance=get_auth_db())
    return {
        "status": "success",
        "completion": res,
        "plan": plan_data
    }

@app.get("/api/students/{student_id}/custom-plans")
def list_student_custom_plans(
    student_id: str,
    session: Dict[str, Any] = Depends(get_current_session)
) -> List[Dict[str, Any]]:
    """Lists private custom improvement tasks for the authenticated student."""
    clean_id = student_id.strip().upper()
    if session.get("role") != "student" or session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to access your own custom plans."
        )

    return get_auth_db().get_custom_plans(clean_id)

@app.post("/api/students/{student_id}/custom-plans", status_code=status.HTTP_201_CREATED)
def create_student_custom_plan(
    student_id: str,
    req: CustomPlanCreate,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """Creates a new student custom improvement plan in SQLite."""
    clean_id = student_id.strip().upper()
    if session.get("role") != "student" or session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to create plans for your own account."
        )

    if not req.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required and cannot be blank."
        )

    new_plan = get_auth_db().create_custom_plan(
        student_id=clean_id,
        title=req.title,
        description=req.description,
        category=req.category,
        priority=req.priority,
        target_date=req.target_date
    )
    plan_data = service.get_student_improvement_plan(clean_id, auth_db_instance=get_auth_db())
    return {
        "status": "success",
        "plan": new_plan,
        "summary": plan_data
    }

@app.put("/api/students/{student_id}/custom-plans/{plan_id}")
def update_student_custom_plan(
    student_id: str,
    plan_id: str,
    req: CustomPlanUpdate,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """Updates fields or completion status of an existing student custom plan."""
    clean_id = student_id.strip().upper()
    if session.get("role") != "student" or session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to modify your own plans."
        )

    updates = req.model_dump(exclude_unset=True)
    if "title" in updates and not updates["title"].strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty."
        )

    updated_plan = get_auth_db().update_custom_plan(
        student_id=clean_id,
        plan_id=plan_id,
        updates=updates
    )
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom plan with ID '{plan_id}' not found for student '{student_id}'."
        )

    plan_data = service.get_student_improvement_plan(clean_id, auth_db_instance=get_auth_db())
    return {
        "status": "success",
        "plan": updated_plan,
        "summary": plan_data
    }

@app.delete("/api/students/{student_id}/custom-plans/{plan_id}")
def delete_student_custom_plan(
    student_id: str,
    plan_id: str,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """Deletes a student custom improvement plan from SQLite."""
    clean_id = student_id.strip().upper()
    if session.get("role") != "student" or session["student_id"] != clean_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are only authorized to delete your own plans."
        )

    deleted = get_auth_db().delete_custom_plan(clean_id, plan_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom plan with ID '{plan_id}' not found for student '{student_id}'."
        )

    plan_data = service.get_student_improvement_plan(clean_id, auth_db_instance=get_auth_db())
    return {
        "status": "success",
        "deleted_id": plan_id,
        "summary": plan_data
    }

# -----------------------------------------------------------------------------
# Faculty-Only Management Endpoints (Strictly Protected)
# -----------------------------------------------------------------------------
@app.post("/api/faculty/students/{student_id}/records")
def update_student_records(
    student_id: str,
    req: FacultyUpdateRequest,
    session: Dict[str, Any] = Depends(get_current_session)
) -> Dict[str, Any]:
    """
    Faculty-only endpoint to persistently update a student's marks and attendance.
    Strictly verifies faculty role on the backend (returns 403 for students).
    Validates all inputs, saves to SQLite, and triggers analytics recalculation.
    """
    if session.get("role") != "faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Faculty authorization required to modify student academic and attendance records."
        )

    clean_id = student_id.strip().upper()
    if clean_id not in service.student_dossiers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record with ID '{student_id}' not found."
        )

    acad_list = [item.model_dump() for item in req.academic_updates] if req.academic_updates else None
    att_list = [item.model_dump() for item in req.attendance_updates] if req.attendance_updates else None

    try:
        updated_dossier = service.update_student_records(
            student_id=clean_id,
            academic_updates=acad_list,
            attendance_updates=att_list,
            auth_db_instance=get_auth_db()
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    return {
        "status": "success",
        "message": f"Academic and attendance records for {clean_id} updated successfully.",
        "student": updated_dossier,
        "updated_profile": updated_dossier
    }

@app.get("/api/analytics/summary")
def get_cohort_summary() -> Dict[str, Any]:
    """Returns cohort-wide distributions, averages, and department summaries."""
    return service.get_cohort_summary()

# -----------------------------------------------------------------------------
# Static Single Page Application (SPA) Mount
# -----------------------------------------------------------------------------
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
