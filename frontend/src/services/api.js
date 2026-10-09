/**
 * api.js
 * API client for Smart Campus Analytics backend endpoints with session token management.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';
export const SESSION_STORAGE_KEY = 'smart_campus_session_id';

export function getSessionToken() {
  return localStorage.getItem(SESSION_STORAGE_KEY);
}

export function setSessionToken(token) {
  if (token) {
    localStorage.setItem(SESSION_STORAGE_KEY, token);
  } else {
    localStorage.removeItem(SESSION_STORAGE_KEY);
  }
}

function getAuthHeaders() {
  const token = getSessionToken();
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  if (!res.ok) throw new Error('API Health check failed');
  return res.json();
}

export async function loginStudent(username, password) {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Invalid username or password' }));
    throw new Error(err.detail || 'Login failed');
  }
  const data = await res.json();
  const token = data.token || data.session_id;
  setSessionToken(token);
  return data;
}

export async function fetchCurrentUser() {
  const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    if (res.status === 401) {
      setSessionToken(null);
      return null;
    }
    throw new Error('Failed to validate session');
  }
  return res.json();
}

export async function logoutStudent() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    setSessionToken(null);
    return res.json();
  } catch (e) {
    setSessionToken(null);
    return { status: 'logged_out' };
  }
}

export async function fetchLoginHistory() {
  const res = await fetch(`${API_BASE_URL}/api/auth/history`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    if (res.status === 401) {
      setSessionToken(null);
      throw new Error('Session expired');
    }
    throw new Error('Failed to fetch login history');
  }
  return res.json();
}

export async function updatePassword(currentPassword, newPassword, confirmPassword) {
  const res = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to update password' }));
    throw new Error(err.detail || 'Failed to update password');
  }
  return res.json();
}

export async function fetchStudents(params = {}) {
  const query = new URLSearchParams(params).toString();
  const url = `${API_BASE_URL}/api/students${query ? `?${query}` : ''}`;
  const res = await fetch(url, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch students list');
  return res.json();
}

export async function updateStudentRecords(studentId, payload) {
  const res = await fetch(`${API_BASE_URL}/api/faculty/students/${studentId}/records`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to update student records' }));
    throw new Error(err.detail || 'Failed to update student records');
  }
  return res.json();
}

export async function fetchStudentProfile(studentId) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    if (res.status === 401) {
      setSessionToken(null);
      throw new Error('Session expired. Please log in again.');
    }
    if (res.status === 403) {
      throw new Error('Access denied: You are only authorized to access your own student profile.');
    }
    if (res.status === 404) {
      throw new Error(`Student ${studentId} not found`);
    }
    throw new Error('Failed to fetch student profile');
  }
  return res.json();
}

export async function fetchStudentScore(studentId) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/score`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch student score');
  return res.json();
}

export async function fetchStudentRisks(studentId) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/risks`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch student risks');
  return res.json();
}

export async function fetchStudentRecommendations(studentId) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/recommendations`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch recommendations');
  return res.json();
}

export async function fetchCohortSummary() {
  const res = await fetch(`${API_BASE_URL}/api/analytics/summary`);
  if (!res.ok) throw new Error('Failed to fetch cohort summary');
  return res.json();
}

export async function fetchImprovementPlan(studentId) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/improvement-plan`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to fetch improvement plan' }));
    throw new Error(err.detail || 'Failed to fetch improvement plan');
  }
  return res.json();
}

export async function updateRecommendationStatus(studentId, recommendationId, status) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/recommendations/${recommendationId}/status`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to update recommendation status' }));
    throw new Error(err.detail || 'Failed to update recommendation status');
  }
  return res.json();
}

export async function fetchCustomPlans(studentId) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/custom-plans`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to fetch custom plans' }));
    throw new Error(err.detail || 'Failed to fetch custom plans');
  }
  return res.json();
}

export async function createCustomPlan(studentId, planData) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/custom-plans`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(planData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to create custom plan' }));
    throw new Error(err.detail || 'Failed to create custom plan');
  }
  return res.json();
}

export async function updateCustomPlan(studentId, planId, planData) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/custom-plans/${planId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(planData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to update custom plan' }));
    throw new Error(err.detail || 'Failed to update custom plan');
  }
  return res.json();
}

export async function deleteCustomPlan(studentId, planId) {
  const res = await fetch(`${API_BASE_URL}/api/students/${studentId}/custom-plans/${planId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to delete custom plan' }));
    throw new Error(err.detail || 'Failed to delete custom plan');
  }
  return res.json();
}
