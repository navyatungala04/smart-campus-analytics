# Smart Campus Analytics: Predict, Optimize & Improve Student Success

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19.x-61dafb.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.x-646cff.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind-v4.x-38bdf8.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Pytest Tests](https://img.shields.io/badge/pytest-82%20passed-brightgreen.svg)]()
[![Validation Status](https://img.shields.io/badge/data%20validation-52%2F52%20passed-success.svg)]()
[![Auth Database](https://img.shields.io/badge/SQLite-sessions%20%26%20custom%20plans-orange.svg)]()

Smart Campus Analytics is an intelligent, student-centric academic intelligence and career readiness web platform. It consolidates fragmented campus touchpoints into a unified 360-degree student profile to diagnose performance bottlenecks, forecast risks, deliver actionable growth plans, and provide a secure, persistent student authentication system with personal session audit logs and self-service password management.

---

## 🎯 Primary User Persona: The Student

This platform is engineered specifically for **undergraduate engineering students**. It enables students to:
1. **Understand Holistic Performance:** Track a multi-dimensional **Student Success Score (0–100)** spanning academics, attendance, LMS coursework, engagement, placements, and soft skills.
2. **Gain Actionable Visibility:** Unpack transparent score breakdowns to see exact percentage contributions from each dimension.
3. **Catch Academic & Career Vulnerabilities Early:** Receive explainable diagnostic risk alerts (High, Moderate, Low) with explicit triggers and safe thresholds.
4. **Follow Tailored Roadmaps:** Execute personalized, measurable improvement tasks (e.g., exact consecutive classes needed to surpass the 75% attendance threshold).
5. **Secure Individual Student Sign-In & Credential Control:** Authenticate using persistent credentials, update passwords securely with complexity validation, restore sessions across page refreshes, and track personal login audit history.

---

## 🔐 Username, Password Authentication & Change Password Feature

The application features a secure, backend-verified username-and-password authentication system and a dedicated **Change Password** security module backed by SQLite (`data/auth.db`), excluded from Git.

### 1. Professional Login Page
* **Unauthenticated Access:** Users who are not logged in are presented with the dedicated login screen.
* **Fields & Controls:** Includes a **Username or Student ID** field, a **Password** field with a **Show/Hide Password** toggle control (`Eye`/`EyeOff`), and a **Sign In** action button.
* **Validation:** Validates empty fields on submission, catches incorrect credentials with clear error feedback, and blocks unauthorized access.
* **No Auto-Login or Persona Shortcuts:** Quick-login persona buttons and automatic student selection dropdowns have been removed. The login page never auto-selects or automatically logs in as Karthik Sharma, Naveen Das, or any other student.
* **Source Code Cleanliness:** No real credentials are hardcoded in frontend source code.

### 2. Change Password Feature (Sidebar & Profile)
Located under the **Account** section in the navigation sidebar (**"Change Password"**) and accessible via a button on the **My Profile** page:
* **Form Inputs:**
  * **Current Password** (with Show/Hide toggle)
  * **New Password** (with Show/Hide toggle)
  * **Confirm New Password** (with Show/Hide toggle)
  * **Update Password** submit button
* **Password Conditions (Validated on Frontend & Backend):**
  1. At least 8 characters
  2. At least one uppercase letter (`A-Z`)
  3. At least one lowercase letter (`a-z`)
  4. At least one number (`0-9`)
  5. At least one special character (`@`, `#`, `$`, `!`, etc.)
* **Real-Time Interactive Feedback:** As the student types their new password, an interactive checklist dynamically displays checkmarks for each satisfied condition along with password match verification.
* **Backend Security Enforcement:**
  * The current password is verified against the authenticated user's stored salt and PBKDF2 hash.
  * Rejects incorrect current passwords, weak passwords, and mismatched confirmations with clear error messages.
  * Generates a fresh 16-byte cryptographic salt and computes a new PBKDF2-HMAC-SHA256 hash (`100,000` rounds).
  * Updates only the authenticated user's record in SQLite (`data/auth.db`).
  * Never returns hashes or cryptographic salts to the client.
* **Persistence Across Restarts:** Changed passwords persist indefinitely in SQLite and are never overwritten by server restarts or database seeding scripts.
* **Login Behavior:** Once updated, the student must authenticate using their new password; the old password is immediately invalidated.

---

## 🔑 Demo Accounts & Testing Credentials

All 120 fictional students from `data/students.csv` have pre-configured student accounts in `data/auth.db`.

### Documented Initial Demo Credentials
The initial password for all pre-seeded demo accounts is:
```text
Password: campus123
```

#### Featured Test Personas
| Persona | Student Name | Username / ID | Initial Password | Key Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **⭐ High Achiever** | Naveen Das | `stu1015` or `STU1015` | `campus123` | Score: 88.96, CGPA: 9.38, 0 Backlogs, Low Risk |
| **⚠️ At-Risk Student** | Rhea Kumar | `stu1008` or `STU1008` | `campus123` | Score: 43.09, CGPA: 4.65, 2 Backlogs, High Risk |
| **⚖️ Steady Performer** | Surya Kumar | `stu1002` or `STU1002` | `campus123` | Score: 74.82, CGPA: 7.58, Attendance: 82.1%, Low Risk |
| **💻 Practical Specialist** | Dev Patel | `stu1036` or `STU1036` | `campus123` | Coding: 95.2, Hackathons: 5, Moderate CGPA |

*Additional accounts:* Any student from `STU1001` through `STU1120` can be logged into using username `stu<ID>` (e.g. `stu1001`) with initial password `campus123`.

### Account Management CLI (`scripts/manage_auth.py`)
To manage, verify, create, or change passwords via CLI:

```bash
# Verify login credentials:
python scripts/manage_auth.py --verify stu1015 campus123

# Change password with current password verification:
python scripts/manage_auth.py --change-password stu1015 campus123 NewStrong#Pass2026

# Reset a student's password:
python scripts/manage_auth.py --reset-password stu1015 campus123

# List demo personas and summary:
python scripts/manage_auth.py --list

# Sync or initialize demo accounts from CSV:
python scripts/manage_auth.py --init
```

---

## 🏗️ Project Architecture

```text
SmartCampusAnalytics/
├── backend/
│   └── main.py                       # FastAPI application serving REST endpoints, Auth & static SPA
├── data/
│   ├── auth.db                       # SQLite database storing hashed credentials & session history (git-ignored)
│   ├── students.csv                  # Master demographic directory (120 fictional students)
│   ├── academic.csv                  # Subject-wise marks, CGPA, and backlog tracking
│   ├── attendance.csv                # Course attendance logs and percentages
│   ├── lms_activity.csv              # Online portal logins and assignment submissions
│   ├── engagement.csv                # Co-curricular events, clubs, hackathons, certs
│   ├── placement.csv                 # Aptitude, coding, and mock interview assessments
│   ├── skills.csv                    # Domain technical and behavioral soft skills
│   ├── feedback.csv                  # Faculty mentor appraisal & student satisfaction
│   └── processed/                    # Processed analytics outputs
│       ├── unified_student_profiles.csv   # Unified master dataframe (120 rows, 57 features)
│       ├── student_risk_assessments.csv   # Academic and placement risk levels & summaries
│       ├── student_recommendations.csv    # Flattened prioritized recommendations
│       └── unified_analytics_master.json  # Full JSON schema ready for API responses
├── docs/
│   ├── dataset_documentation.md      # Phase 1 dataset schemas, types, and ER diagrams
│   ├── scoring_methodology.md        # Phase 2 Success Score formulas, weights, and policies
│   └── risk_methodology.md           # Phase 2 risk rules, thresholds, and segmentation
├── frontend/                         # React.js + Vite student-facing web application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # Authenticated student header with profile card & logout
│   │   │   └── Sidebar.jsx           # 13-page navigation menu with client-side routing
│   │   ├── pages/
│   │   │   ├── Login.jsx             # Professional login screen (Username, Password, Show/Hide)
│   │   │   ├── Dashboard.jsx         # 1. Student Dashboard (Overview & 7-axis radar)
│   │   │   ├── Academic.jsx          # 2. Academic Performance & Subject Breakdown
│   │   │   ├── Attendance.jsx        # 3. Attendance Monitoring & 75% Cutoff Calculator
│   │   │   ├── LmsEngagement.jsx     # 4. LMS Coursework & Extracurriculars
│   │   │   ├── Placement.jsx         # 5. Placement Readiness & Coding Benchmarks
│   │   │   ├── Skills.jsx            # 6. Skills Profiling & Verified Credentials
│   │   │   ├── Feedback.jsx          # 7. Institutional & Mentorship Feedback
│   │   │   ├── SuccessScore.jsx      # 8. My Success Score Breakdown & Weights Table
│   │   │   ├── RiskAnalysis.jsx      # 9. My Risk Analysis & Trigger Diagnostics
│   │   │   ├── ImprovementPlan.jsx   # 10. My Improvement Plan (Interactive Checklist)
│   │   │   ├── Profile.jsx           # 11. My Profile & Demo Verification Card
│   │   │   ├── ChangePassword.jsx    # 12. Change Password Page (Conditions checklist & form)
│   │   │   └── LoginHistory.jsx      # 13. Login History & Session Audit Trail
│   │   ├── services/
│   │   │   └── api.js                # API client transmitting session token headers
│   │   ├── App.jsx                   # Layout, auth state controller, and client-side router
│   │   ├── index.css                 # Tailwind CSS v4 setup and utility classes
│   │   └── main.jsx                  # React application entry point
│   ├── dist/                         # Compiled production assets served by FastAPI
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── .env
├── scripts/
│   ├── generate_synthetic_data.py    # Phase 1 synthetic data generator
│   ├── run_pipeline.py               # Phase 2 end-to-end integration and export runner
│   └── manage_auth.py                # Account management & credential verification CLI
├── src/
│   ├── __init__.py                   # Package exports
│   ├── auth_db.py                    # SQLite authentication manager, password hasher & validator
│   ├── config.py                     # Configurable weights, thresholds, and benchmarks
│   ├── data_loader.py                # Ingestion, duplicate checks, referential integrity
│   ├── integrator.py                 # Multi-level aggregations without student double-counting
│   ├── scoring.py                    # Success Score calculator with missing data re-weighting
│   ├── risk_analyzer.py              # Rule-based Academic and Placement risk diagnostics
│   ├── segmentation.py               # 2D performance matrix cohort segmentation
│   ├── recommendations.py            # Dynamic, measurable recommendation engine
│   └── service.py                    # AnalyticsService facade integrating all modules
├── tests/
│   ├── test_api.py                   # FastAPI REST endpoints & 404 handling tests
│   ├── test_auth.py                  # Auth, session, isolation & password change tests (16 tests)
│   ├── test_integration.py           # Ingestion, aggregation, and integrity tests
│   ├── test_scoring.py               # Score bounds, weights, and missing data tests
│   ├── test_risk_analysis.py         # Academic & placement rule verification
│   ├── test_segmentation.py          # Persona classification matrix tests
│   ├── test_recommendations.py       # Actionable plan & target calculation tests
│   └── test_service.py               # Service facade and invalid ID handling tests
├── validate_data.py                  # Phase 1 automated dataset validation suite
├── .env.example                      # Root environment configuration template
├── .gitignore                        # Standard project git exclusions (including *.db)
└── README.md                         # Project documentation
```

---

## ⚡ Quickstart & Installation

### 1. Prerequisites
* **Python:** 3.10+ (tested on Python 3.13)
* **Node.js:** v18+ (tested on Node v24.15) and npm

### 2. Install Backend Dependencies
From the project root:

```bash
python -m pip install fastapi uvicorn pandas numpy pytest httpx
```

### 3. Install Frontend Dependencies & Build Production Assets
From the `frontend/` directory:

```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 🚀 Running the Application

### Option A: Unified Production Server (Recommended Single Terminal)
Since the production frontend is pre-built into `frontend/dist/`, FastAPI serves both the REST API and the frontend application on port 8000:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
* Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.
* API Interactive Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Option B: Separate Terminals (Frontend Development Mode)

#### Terminal 1 — Start the FastAPI Backend:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2 — Start Vite Development Server:
```bash
cd frontend
npm run dev
```
* Access Vite dev server at [http://localhost:5173/](http://localhost:5173/)

---

## 🧪 Running Automated Tests

### 1. Full Pytest Suite (53 Tests)
Runs all unit and integration tests covering data integration, success score calculations, risk diagnostics, recommendation targets, and all 16 authentication & password management tests:

```bash
python -m pytest -v
```

### 2. Dedicated Authentication & Password Change Tests (16 Tests in `tests/test_auth.py`)
```bash
python -m pytest tests/test_auth.py -v
```
Verifies:
* `test_login_with_valid_username_and_password`: Validates password hashing and token generation.
* `test_login_with_incorrect_password`: Rejects wrong passwords with 401.
* `test_login_with_unknown_username`: Rejects non-existent usernames with 401.
* `test_login_with_empty_fields`: Validates input requirements with 400.
* `test_refreshing_dashboard_while_logged_in`: Restores user session without requiring re-login.
* `test_logging_out_and_logging_in_as_another_student`: Verifies session termination and switching accounts.
* `test_blocking_dashboard_and_api_access_without_authentication`: Rejects unauthenticated requests with 401.
* `test_preventing_one_student_from_accessing_another_students_information`: Enforces 403 when trying to access other student IDs.
* `test_preserving_login_history_in_sqlite`: Verifies login history persistence in SQLite across service restarts.
* `test_change_password_success_and_login_with_new_password`: Verifies password change, old password invalidation, and login with new password.
* `test_change_password_incorrect_current_password`: Verifies rejection when current password is wrong.
* `test_change_password_weak_passwords_rejection`: Verifies rejection for passwords violating any of the 5 conditions.
* `test_change_password_mismatched_confirmation`: Verifies rejection when new password and confirm password differ.
* `test_change_password_unauthenticated_rejected`: Rejects unauthenticated password update requests with 401.
* `test_change_password_persistence_and_no_overwrite_on_reinit`: Asserts changed passwords persist across backend restarts and seeding.
* `test_change_password_user_isolation`: Asserts updating one student's password does not alter another student's credentials.

### 3. Raw Data Integrity Validation (52 Checks)
```bash
python validate_data.py
```

---

## 🧭 Student Pages Overview (13 Views)

| Page | View Name | Key Content & Interactive Capabilities |
| :---: | :--- | :--- |
| **1** | **Student Dashboard** | Holistic 360° overview, 7-axis competency radar chart, semester subject marks preview, top KPI cards, risk diagnostic alert banner, and top recommendations. |
| **2** | **Academic Performance** | Cumulative GPA (scale of 10), active backlogs status, marks range, and detailed semester subject-by-subject table with pass/fail badges. |
| **3** | **Attendance** | Overall attendance percentage, attended vs scheduled lectures, subject-by-subject attendance table, 75% cutoff reference bar chart, and **consecutive classes needed calculator**. |
| **4** | **LMS & Engagement** | Monthly digital login frequency meter, assignment completion rate (% and pending count), campus events, clubs active, hackathons participated, and extracurricular tier badge. |
| **5** | **Placement Readiness** | Composite Placement Readiness Index (0-100), quantitative aptitude score, algorithmic coding score, mock interview evaluation status, and recruitment benchmark chart. |
| **6** | **Skills & Certifications** | Department technical domain score, soft skills appraisal, verified industry MOOC credentials count, and evaluated skills tag matrix. |
| **7** | **Feedback Insights** | Faculty mentor rating (1.0–5.0 with scaled percentage), optional student satisfaction rating, feedback submission timestamps, and advisor remarks. |
| **8** | **My Success Score** | Transparent breakdown table showing raw scores, configured category weights (summing to 100%), weighted point contributions, and formula explanations. |
| **9** | **My Risk Analysis** | Academic and Placement risk diagnostics (High, Moderate, Low) with explicit list of triggered indicators, student values, and safe thresholds. |
| **10** | **My Improvement Plan** | Consolidated roadmap combining AI-generated diagnostic recommendations and student-created custom tasks. Features persistent completion tracking in SQLite, "Add My Own Plan" modal, category & priority tags, overdue alerts, and completion percentage progress bar. |
| **11** | **My Profile** | Student demographic card (Name, ID, Department, Year, Semester, University Email), persona badge, demo verification notice, and **Change Password** action button. |
| **12** | **Change Password** | Dedicated security page with Current Password, New Password, Confirm New Password, independent Show/Hide toggles, and live 5-point condition checklist. |

---

## 🔌 API Endpoints Reference

All endpoints return real data computed by `AnalyticsService` and authenticated via `AuthDatabase`:

| Method | Endpoint | Protection | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Public | Authenticates student username/ID & password, returns session token |
| `GET` | `/api/auth/me` | Bearer Token | Validates session token, returns authenticated student profile & session info |
| `POST` | `/api/auth/logout` | Bearer Token | Invalidates active session in SQLite and records logout timestamp |
| `POST` | `/api/auth/change-password` | Bearer Token | Securely updates authenticated student's password after verifying current credentials & complexity |
| `GET` | `/api/auth/history` | Bearer Token | Returns historical login sessions scoped strictly to authenticated student |
| `GET` | `/api/health` | Public | Service health status and student count |
| `GET` | `/api/students` | Protected | Student roster with department, CGPA, and risk levels |
| `GET` | `/api/students/{id}` | Protected | Complete 360-degree student profile dossier (verified against session) |
| `GET` | `/api/students/{id}/score` | Protected | Student Success Score and component breakdown |
| `GET` | `/api/students/{id}/risks` | Protected | Academic and Placement risk assessments with triggers |
| `GET` | `/api/students/{id}/recommendations` | Protected | List of prioritized, personalized action items with persistent completion state |
| `GET` | `/api/students/{id}/improvement-plan` | Protected | Consolidated Improvement Plan with system recommendations, custom tasks, and stats |
| `POST` | `/api/students/{id}/recommendations/{rec_id}/status` | Protected | Persistently updates completion status (`completed` or `pending`) for system recommendations |
| `GET` | `/api/students/{id}/custom-plans` | Protected | Retrieves list of student's private custom improvement tasks |
| `POST` | `/api/students/{id}/custom-plans` | Protected | Creates a new personal custom improvement task |
| `PUT` | `/api/students/{id}/custom-plans/{plan_id}` | Protected | Updates fields or status of a custom improvement task |
| `DELETE` | `/api/students/{id}/custom-plans/{plan_id}` | Protected | Deletes a custom improvement task |
| `POST` | `/api/faculty/students/{id}/records` | Faculty Only | Updates subject marks and attendance records; recalculates analytics pipeline |
| `GET` | `/api/analytics/summary` | Public | Cohort-wide distributions, averages, and quartiles |
