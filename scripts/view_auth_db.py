"""
view_auth_db.py
Read-Only SQLite Database Viewer for Smart Campus Analytics (data/auth.db).
Displays users and sessions tables, active session tracking, search, and live refresh.
Does not depend on any VS Code extension. Never exposes plaintext passwords or tokens.
"""

import os
import sys
import json
import sqlite3
import argparse
import webbrowser
from datetime import datetime
from typing import Dict, Any, List, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.auth_db import hash_password, DEFAULT_DEMO_PASSWORD

AUTH_DB_PATH = os.path.join(PROJECT_ROOT, "data", "auth.db")
HTML_EXPORT_PATH = os.path.join(PROJECT_ROOT, "data", "auth_viewer.html")

def fetch_auth_data(db_path: str = AUTH_DB_PATH) -> Dict[str, Any]:
    """
    Queries data/auth.db strictly in read-only mode (mode=ro).
    Extracts sanitized and masked data for users and sessions tables.
    Never exposes raw password hashes, salts, or full session tokens.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")

    # Connect strictly in read-only mode using SQLite URI
    uri = f"file:{os.path.abspath(db_path)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Identify which accounts have active sessions
    cursor.execute("SELECT DISTINCT student_id FROM sessions WHERE status = 'active'")
    active_student_ids = {r[0] for r in cursor.fetchall()}

    # 2. Query Users table
    cursor.execute("""
        SELECT student_id, username, student_name, password_hash, salt, created_at 
        FROM users 
        ORDER BY student_id ASC
    """)
    users_raw = cursor.fetchall()
    users: List[Dict[str, Any]] = []
    default_pwd_count = 0
    changed_pwd_count = 0

    for r in users_raw:
        # Check if password is the default demo password without exposing hash or salt
        is_default = (r["password_hash"] == hash_password(DEFAULT_DEMO_PASSWORD, r["salt"]))
        if is_default:
            default_pwd_count += 1
            pwd_status_badge = "Default Demo (campus123)"
            pwd_is_changed = False
        else:
            changed_pwd_count += 1
            pwd_status_badge = "Custom Password (Changed)"
            pwd_is_changed = True

        has_active = r["student_id"] in active_student_ids
        uname = r["username"] if ("username" in r.keys() and r["username"]) else r["student_id"].lower()

        users.append({
            "student_id": r["student_id"],
            "username": uname,
            "student_name": r["student_name"],
            "created_at": r["created_at"],
            "password_display": "●●●●●●●● (Password stored as secure PBKDF2 hash)",
            "password_status": pwd_status_badge,
            "password_is_changed": pwd_is_changed,
            "has_active_session": has_active
        })

    # 3. Query Sessions table
    cursor.execute("""
        SELECT session_id, student_id, username, student_name, login_timestamp, logout_timestamp, 
               status, ip_address, user_agent 
        FROM sessions 
        ORDER BY login_timestamp DESC
    """)
    sessions_raw = cursor.fetchall()
    sessions: List[Dict[str, Any]] = []
    active_sessions_count = 0
    logged_out_sessions_count = 0
    browser_sessions_count = 0
    test_sessions_count = 0

    for r in sessions_raw:
        sid = r["session_id"] or ""
        masked_token = f"{sid[:8]}...[Protected Token]" if len(sid) >= 8 else "—"

        status = r["status"]
        if status == "active":
            active_sessions_count += 1
            dur_display = "Active Now"
        else:
            logged_out_sessions_count += 1
            dur_display = "Concluded"
            if r["logout_timestamp"] and r["login_timestamp"]:
                try:
                    t_in = datetime.fromisoformat(r["login_timestamp"])
                    t_out = datetime.fromisoformat(r["logout_timestamp"])
                    sec = max(0, int((t_out - t_in).total_seconds()))
                    if sec < 60:
                        dur_display = f"{sec}s"
                    elif sec < 3600:
                        dur_display = f"{sec // 60}m {sec % 60}s"
                    else:
                        dur_display = f"{sec // 3600}h {(sec % 3600) // 60}m"
                except Exception:
                    pass

        ua = r["user_agent"] or ""
        if "Chrome" in ua or "Firefox" in ua or "Safari" in ua or "Mozilla" in ua:
            client_type = "Browser (Chrome/Web)"
            browser_sessions_count += 1
        elif "testclient" in ua.lower():
            client_type = "Automated Test Client"
            test_sessions_count += 1
        else:
            client_type = "Direct Client / CLI"

        uname = r["username"] if ("username" in r.keys() and r["username"]) else r["student_id"].lower()

        sessions.append({
            "session_id_masked": masked_token,
            "student_id": r["student_id"],
            "username": uname,
            "student_name": r["student_name"] or r["student_id"],
            "login_timestamp": r["login_timestamp"],
            "logout_timestamp": r["logout_timestamp"] or "—",
            "status": status,
            "duration": dur_display,
            "ip_address": r["ip_address"] or "—",
            "client_type": client_type,
            "user_agent": ua
        })

    conn.close()

    return {
        "metadata": {
            "database_file": os.path.relpath(db_path, PROJECT_ROOT).replace("\\", "/"),
            "database_full_path": os.path.abspath(db_path),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "read_only": True
        },
        "stats": {
            "total_users": len(users),
            "users_with_active_sessions": len(active_student_ids),
            "default_password_count": default_pwd_count,
            "changed_password_count": changed_pwd_count,
            "total_sessions": len(sessions),
            "active_sessions": active_sessions_count,
            "logged_out_sessions": logged_out_sessions_count,
            "browser_sessions": browser_sessions_count,
            "test_sessions": test_sessions_count
        },
        "users": users,
        "sessions": sessions
    }

def generate_html_viewer(data: Dict[str, Any]) -> str:
    """Generates a standalone, beautiful HTML document with search, filters, and refresh support."""
    data_json = json.dumps(data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Campus Analytics - Authentication Database Viewer (data/auth.db)</title>
  <style>
    :root {{
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --success: #059669;
      --success-bg: #ecfdf5;
      --warning: #d97706;
      --warning-bg: #fffbeb;
      --gray-bg: #f1f5f9;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      padding: 24px;
      line-height: 1.5;
    }}
    .container {{ max-width: 1360px; margin: 0 auto; }}
    
    /* Header */
    .header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
    }}
    .title-area h1 {{
      font-size: 24px;
      font-weight: 800;
      color: #1e1b4b;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .badge-ro {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      background: #e0e7ff;
      color: #3730a3;
      padding: 3px 10px;
      border-radius: 9999px;
      border: 1px solid #c7d2fe;
    }}
    .title-area p {{
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 4px;
    }}
    .actions {{ display: flex; align-items: center; gap: 12px; }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 18px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text-main);
      transition: all 0.15s ease;
    }}
    .btn:hover {{ background: #f1f5f9; }}
    .btn-primary {{
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }}
    .btn-primary:hover {{ background: var(--primary-hover); }}

    /* KPI Summary Cards */
    .grid-stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .stat-label {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 6px;
    }}
    .stat-val {{
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
    }}
    .stat-sub {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 4px;
    }}

    /* Search & Filter Bar */
    .controls-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 24px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}
    .search-box {{
      flex: 1;
      min-width: 260px;
      position: relative;
    }}
    .search-box input {{
      width: 100%;
      padding: 10px 14px 10px 38px;
      font-size: 13px;
      border: 1px solid var(--border);
      border-radius: 8px;
      outline: none;
      transition: border 0.15s;
    }}
    .search-box input:focus {{ border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79,70,229,0.1); }}
    .search-box svg {{
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      width: 16px;
      height: 16px;
      fill: var(--text-muted);
    }}
    .tab-pills {{ display: flex; gap: 8px; }}
    .tab-pill {{
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text-muted);
      cursor: pointer;
    }}
    .tab-pill.active {{
      background: #1e1b4b;
      color: #fff;
      border-color: #1e1b4b;
    }}

    /* Table Sections */
    .section-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .section-header {{
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #fcfdfe;
    }}
    .section-title {{
      font-size: 16px;
      font-weight: 700;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .section-count {{
      font-size: 12px;
      font-weight: 600;
      background: #f1f5f9;
      color: #475569;
      padding: 2px 8px;
      border-radius: 6px;
    }}
    .table-container {{
      max-height: 520px;
      overflow-y: auto;
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #f8fafc;
      color: #475569;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      z-index: 10;
    }}
    td {{
      padding: 12px 16px;
      border-bottom: 1px solid #f1f5f9;
      color: #1e293b;
      white-space: nowrap;
    }}
    tr:hover td {{ background: #f8fafc; }}
    
    /* Badges */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 9px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 600;
    }}
    .badge-active {{ background: var(--success-bg); color: var(--success); border: 1px solid #a7f3d0; }}
    .badge-logged-out {{ background: var(--gray-bg); color: #475569; border: 1px solid #cbd5e1; }}
    .badge-default {{ background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }}
    .badge-changed {{ background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; }}
    .dot {{ width: 6px; height: 6px; border-radius: 50%; }}
    .dot-green {{ background: var(--success); box-shadow: 0 0 0 2px #d1fae5; }}
    .dot-gray {{ background: #94a3b8; }}

    /* Security Notice */
    .notice {{
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #166534;
      border-radius: 10px;
      padding: 14px 18px;
      font-size: 12.5px;
      margin-bottom: 24px;
      display: flex;
      gap: 12px;
      align-items: flex-start;
    }}
    .notice-icon {{ font-size: 16px; line-height: 1.4; }}
    .empty-state {{
      padding: 40px;
      text-align: center;
      color: var(--text-muted);
      font-size: 13px;
    }}
  </style>
</head>
<body>

<div class="container">
  
  <!-- Header -->
  <header class="header">
    <div class="title-area">
      <h1>
        <span>Smart Campus Analytics — SQLite Database Viewer</span>
        <span class="badge-ro">Read-Only Mode</span>
      </h1>
      <p id="meta-text">Target: <strong>data/auth.db</strong> | Generated: {data["metadata"]["generated_at"]}</p>
    </div>
    <div class="actions">
      <button class="btn btn-primary" onclick="refreshData()">
        <svg style="width:14px;height:14px;fill:currentColor;" viewBox="0 0 24 24"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
        <span>Refresh Records</span>
      </button>
    </div>
  </header>

  <!-- Security Banner -->
  <div class="notice">
    <div class="notice-icon">🛡️</div>
    <div>
      <strong>Security & Integrity Protection Active:</strong>
      This viewer connects strictly with <code>mode=ro</code> (Read-Only). No records can be modified, deleted, or reset. Passwords are never stored or displayed in plaintext; all credential entries show a masked PBKDF2 hash indicator. Full secret session tokens are masked to prevent token leakage.
    </div>
  </div>

  <!-- KPI Metrics Grid -->
  <div class="grid-stats">
    <div class="stat-card">
      <div class="stat-label">Registered Students</div>
      <div class="stat-val" id="stat-total-users">{data["stats"]["total_users"]}</div>
      <div class="stat-sub">Accounts in <code>users</code> table</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Accounts with Active Sessions</div>
      <div class="stat-val" style="color:var(--success);" id="stat-active-users">{data["stats"]["users_with_active_sessions"]}</div>
      <div class="stat-sub">Currently logged-in students</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Password Changes</div>
      <div class="stat-val" style="color:#7e22ce;" id="stat-changed-pwd">{data["stats"]["changed_password_count"]}</div>
      <div class="stat-sub">{data["stats"]["default_password_count"]} using default <code>campus123</code></div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Session Records</div>
      <div class="stat-val" id="stat-total-sessions">{data["stats"]["total_sessions"]}</div>
      <div class="stat-sub">Historical logins in SQLite</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Active vs Logged Out</div>
      <div class="stat-val">
        <span style="color:var(--success);" id="stat-active-sess">{data["stats"]["active_sessions"]}</span>
        <span style="color:var(--text-muted);font-size:18px;"> / </span>
        <span style="color:#64748b;" id="stat-logged-sess">{data["stats"]["logged_out_sessions"]}</span>
      </div>
      <div class="stat-sub">Active / Concluded sessions</div>
    </div>
  </div>

  <!-- Controls: Search & Tabs -->
  <div class="controls-card">
    <div class="search-box">
      <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
      <input type="text" id="searchInput" placeholder="Search by username, student ID (e.g. STU1015), or student name..." oninput="onSearch()">
    </div>
    <div class="tab-pills">
      <button class="tab-pill active" id="tab-all" onclick="setTab('all')">View Both Tables</button>
      <button class="tab-pill" id="tab-users" onclick="setTab('users')">Users Table Only</button>
      <button class="tab-pill" id="tab-sessions" onclick="setTab('sessions')">Sessions Table Only</button>
    </div>
  </div>

  <!-- Table 1: Users -->
  <div class="section-card" id="card-users">
    <div class="section-header">
      <div class="section-title">
        <span>Student Users (<code>users</code> Table)</span>
        <span class="section-count" id="count-users">{len(data["users"])} Accounts</span>
      </div>
      <div>
        <label style="font-size:12px;color:var(--text-muted);margin-right:8px;">Filter:</label>
        <select id="userFilter" onchange="renderUsers()" style="padding:4px 8px;font-size:12px;border:1px solid var(--border);border-radius:6px;">
          <option value="all">All Users</option>
          <option value="active_only">Users with Active Sessions Only</option>
          <option value="changed_pwd_only">Changed Passwords Only</option>
        </select>
      </div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Student ID</th>
            <th>Username</th>
            <th>Student Name</th>
            <th>Active Session?</th>
            <th>Password Security</th>
            <th>Password Status</th>
            <th>Account Created</th>
          </tr>
        </thead>
        <tbody id="usersTbody"></tbody>
      </table>
    </div>
  </div>

  <!-- Table 2: Sessions -->
  <div class="section-card" id="card-sessions">
    <div class="section-header">
      <div class="section-title">
        <span>Login Sessions &amp; History (<code>sessions</code> Table)</span>
        <span class="section-count" id="count-sessions">{len(data["sessions"])} Records</span>
      </div>
      <div>
        <label style="font-size:12px;color:var(--text-muted);margin-right:8px;">Filter:</label>
        <select id="sessionFilter" onchange="renderSessions()" style="padding:4px 8px;font-size:12px;border:1px solid var(--border);border-radius:6px;">
          <option value="all">All Sessions</option>
          <option value="active_only">Active Sessions Only</option>
          <option value="logged_out_only">Logged Out Only</option>
          <option value="browser_only">Browser Logins Only (Chrome/Web)</option>
          <option value="test_only">Automated Test Runs Only</option>
        </select>
      </div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Session ID</th>
            <th>Student ID</th>
            <th>Username</th>
            <th>Student Name</th>
            <th>Session Status</th>
            <th>Login Timestamp (UTC)</th>
            <th>Logout Timestamp (UTC)</th>
            <th>Duration</th>
            <th>IP Address</th>
            <th>Client Type</th>
          </tr>
        </thead>
        <tbody id="sessionsTbody"></tbody>
      </table>
    </div>
  </div>

</div>

<script>
  let DB_DATA = {data_json};
  let currentTab = 'all';

  function formatTime(isoStr) {{
    if (!isoStr || isoStr === '—') return '—';
    try {{
      const d = new Date(isoStr);
      return d.toLocaleString([], {{ year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }});
    }} catch(e) {{
      return isoStr;
    }}
  }}

  function renderUsers() {{
    const q = document.getElementById('searchInput').value.trim().toLowerCase();
    const filter = document.getElementById('userFilter').value;
    const tbody = document.getElementById('usersTbody');
    tbody.innerHTML = '';

    const filtered = DB_DATA.users.filter(u => {{
      const matchesSearch = !q || 
        u.student_id.toLowerCase().includes(q) || 
        u.username.toLowerCase().includes(q) || 
        u.student_name.toLowerCase().includes(q);
      
      if (!matchesSearch) return false;
      if (filter === 'active_only' && !u.has_active_session) return false;
      if (filter === 'changed_pwd_only' && !u.password_is_changed) return false;
      return true;
    }});

    document.getElementById('count-users').innerText = `${{filtered.length}} Accounts`;

    if (filtered.length === 0) {{
      tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No matching student user records found.</td></tr>';
      return;
    }}

    filtered.forEach(u => {{
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-family:monospace;font-weight:700;color:#4f46e5;">${{u.student_id}}</td>
        <td style="font-family:monospace;font-weight:600;">${{u.username}}</td>
        <td style="font-weight:600;">${{u.student_name}}</td>
        <td>
          ${{u.has_active_session 
            ? '<span class="badge badge-active"><span class="dot dot-green"></span>Active Now</span>' 
            : '<span class="badge badge-logged-out"><span class="dot dot-gray"></span>Logged Out</span>'}}
        </td>
        <td style="color:#64748b;font-size:12px;">${{u.password_display}}</td>
        <td>
          <span class="badge ${{u.password_is_changed ? 'badge-changed' : 'badge-default'}}">
            ${{u.password_status}}
          </span>
        </td>
        <td style="font-size:12px;color:#64748b;">${{formatTime(u.created_at)}}</td>
      `;
      tbody.appendChild(tr);
    }});
  }}

  function renderSessions() {{
    const q = document.getElementById('searchInput').value.trim().toLowerCase();
    const filter = document.getElementById('sessionFilter').value;
    const tbody = document.getElementById('sessionsTbody');
    tbody.innerHTML = '';

    const filtered = DB_DATA.sessions.filter(s => {{
      const matchesSearch = !q || 
        s.student_id.toLowerCase().includes(q) || 
        s.username.toLowerCase().includes(q) || 
        s.student_name.toLowerCase().includes(q);
      
      if (!matchesSearch) return false;
      if (filter === 'active_only' && s.status !== 'active') return false;
      if (filter === 'logged_out_only' && s.status !== 'logged_out') return false;
      if (filter === 'browser_only' && !s.client_type.includes('Browser')) return false;
      if (filter === 'test_only' && !s.client_type.includes('Test')) return false;
      return true;
    }});

    document.getElementById('count-sessions').innerText = `${{filtered.length}} Records`;

    if (filtered.length === 0) {{
      tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No matching session records found.</td></tr>';
      return;
    }}

    filtered.forEach(s => {{
      const tr = document.createElement('tr');
      const isActive = s.status === 'active';
      tr.innerHTML = `
        <td style="font-family:monospace;font-size:11.5px;color:#64748b;">${{s.session_id_masked}}</td>
        <td style="font-family:monospace;font-weight:700;color:#4f46e5;">${{s.student_id}}</td>
        <td style="font-family:monospace;font-weight:600;">${{s.username}}</td>
        <td style="font-weight:600;">${{s.student_name}}</td>
        <td>
          ${{isActive 
            ? '<span class="badge badge-active"><span class="dot dot-green"></span>Active</span>' 
            : '<span class="badge badge-logged-out"><span class="dot dot-gray"></span>Logged Out</span>'}}
        </td>
        <td style="font-size:12px;">${{formatTime(s.login_timestamp)}}</td>
        <td style="font-size:12px;color:#64748b;">${{formatTime(s.logout_timestamp)}}</td>
        <td style="font-weight:600;font-size:12px;color:${{isActive ? 'var(--success)' : '#475569'}};">${{s.duration}}</td>
        <td style="font-family:monospace;font-size:12px;">${{s.ip_address}}</td>
        <td>
          <span style="font-size:12px;font-weight:500;color:${{s.client_type.includes('Browser') ? '#1e40af' : '#64748b'}};">
            ${{s.client_type}}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    }});
  }}

  function onSearch() {{
    renderUsers();
    renderSessions();
  }}

  function setTab(tab) {{
    currentTab = tab;
    document.querySelectorAll('.tab-pill').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');

    const cardUsers = document.getElementById('card-users');
    const cardSessions = document.getElementById('card-sessions');

    if (tab === 'all') {{
      cardUsers.style.display = 'block';
      cardSessions.style.display = 'block';
    }} else if (tab === 'users') {{
      cardUsers.style.display = 'block';
      cardSessions.style.display = 'none';
    }} else if (tab === 'sessions') {{
      cardUsers.style.display = 'none';
      cardSessions.style.display = 'block';
    }}
  }}

  async function refreshData() {{
    const btn = event?.currentTarget;
    if (btn) btn.innerHTML = '<span>Refreshing...</span>';
    try {{
      // Fetch fresh JSON if served by local server
      const res = await fetch('/api/auth-data');
      if (res.ok) {{
        DB_DATA = await res.json();
        updateStats();
        renderUsers();
        renderSessions();
        if (btn) btn.innerHTML = '<span>Refreshed ✓</span>';
        setTimeout(() => {{ if (btn) btn.innerHTML = '<span>Refresh Records</span>'; }}, 1200);
        return;
      }}
    }} catch(e) {{
      // If loaded as static file, reload window
      window.location.reload();
    }}
  }}

  function updateStats() {{
    document.getElementById('stat-total-users').innerText = DB_DATA.stats.total_users;
    document.getElementById('stat-active-users').innerText = DB_DATA.stats.users_with_active_sessions;
    document.getElementById('stat-changed-pwd').innerText = DB_DATA.stats.changed_password_count;
    document.getElementById('stat-total-sessions').innerText = DB_DATA.stats.total_sessions;
    document.getElementById('stat-active-sess').innerText = DB_DATA.stats.active_sessions;
    document.getElementById('stat-logged-sess').innerText = DB_DATA.stats.logged_out_sessions;
    document.getElementById('meta-text').innerHTML = `Target: <strong>data/auth.db</strong> | Refreshed: ${{new Date().toLocaleTimeString()}}`;
  }}

  // Initial render
  renderUsers();
  renderSessions();
</script>

</body>
</html>
"""
    return html

class AuthViewerServerHandler(BaseHTTPRequestHandler):
    """Simple read-only HTTP handler serving the auth viewer and JSON data API."""

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            try:
                data = fetch_auth_data(AUTH_DB_PATH)
                html = generate_html_viewer(data)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Error loading auth.db: {e}".encode("utf-8"))

        elif self.path.startswith("/api/auth-data"):
            try:
                data = fetch_auth_data(AUTH_DB_PATH)
                payload = json.dumps(data)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                self.wfile.write(payload.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[AUTH-VIEWER] {args[0]} - {args[1]}\n")

def main():
    parser = argparse.ArgumentParser(description="Smart Campus Analytics - Read-Only Database Viewer")
    parser.add_argument("--port", type=int, default=8088, help="Port for the local read-only viewer (default: 8088)")
    parser.add_argument("--export", type=str, default=HTML_EXPORT_PATH, help="Path to export standalone HTML viewer")
    parser.add_argument("--html-only", action="store_true", help="Generate the static HTML viewer file and exit without starting a server")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    print("=" * 70)
    print(" SMART CAMPUS ANALYTICS — AUTHENTICATION DATABASE VIEWER")
    print("=" * 70)
    print(f" Target Database:  {AUTH_DB_PATH}")
    print(f" Access Mode:      READ-ONLY (mode=ro)")

    # 1. Fetch data & export standalone HTML file
    try:
        data = fetch_auth_data(AUTH_DB_PATH)
    except Exception as e:
        print(f"\n[ERROR] Failed to query database: {e}")
        sys.exit(1)

    html_content = generate_html_viewer(data)
    os.makedirs(os.path.dirname(os.path.abspath(args.export)), exist_ok=True)
    with open(args.export, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f" Standalone File:  {os.path.relpath(args.export, PROJECT_ROOT)}")
    print(f" Loaded Records:   {data['stats']['total_users']} users, {data['stats']['total_sessions']} sessions")
    print(f" Active Sessions:  {data['stats']['active_sessions']} active, {data['stats']['logged_out_sessions']} logged out")

    if args.html_only:
        print("\n[SUCCESS] Standalone HTML viewer generated successfully.")
        print(f"To open: file:///{os.path.abspath(args.export).replace(os.sep, '/')}")
        return

    # 2. Start local read-only HTTP server
    server_address = ("127.0.0.1", args.port)
    try:
        httpd = HTTPServer(server_address, AuthViewerServerHandler)
    except OSError as e:
        print(f"\n[WARNING] Could not bind to port {args.port} ({e}).")
        print(f"You can open the generated static file directly in your browser:")
        print(f"  file:///{os.path.abspath(args.export).replace(os.sep, '/')}")
        return

    viewer_url = f"http://127.0.0.1:{args.port}"
    print(f"\n Local Web Server: {viewer_url}")
    print(" Live Features:    Search box, filters, and instant 'Refresh Records' button")
    print(" Press Ctrl+C in this terminal anytime to stop the viewer.\n")

    if not args.no_browser:
        try:
            webbrowser.open(viewer_url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[AUTH-VIEWER] Server stopped.")

if __name__ == "__main__":
    main()
