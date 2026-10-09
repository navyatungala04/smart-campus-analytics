"""
config.py
Configuration parameters, category weights, thresholds, and scoring constants
for Smart Campus Analytics Phase 2.
"""

from typing import Dict, Any

# ==============================================================================
# 1. STUDENT SUCCESS SCORE CATEGORY WEIGHTS (Sum strictly equals 1.00 / 100%)
# ==============================================================================
CATEGORY_WEIGHTS: Dict[str, float] = {
    "academic": 0.25,        # Academic Performance (CGPA, marks, backlog penalty)
    "attendance": 0.15,      # Attendance Percentage across enrolled courses
    "lms_activity": 0.10,    # Online portal login frequency and assignment completion
    "engagement": 0.10,      # Co-curricular, clubs, hackathons, certifications
    "placement": 0.20,       # Placement aptitude, coding, mock interview readiness
    "skills": 0.12,          # Technical competency and soft skills profiling
    "feedback": 0.08,        # Institutional mentorship & student satisfaction rating
}

# Assert weights sum to 1.0 within floating point precision
assert abs(sum(CATEGORY_WEIGHTS.values()) - 1.0) < 1e-6, "Category weights must sum to 1.00"

# ==============================================================================
# 2. SUB-INDICATOR WEIGHTS & NORMALIZATION BENCHMARKS
# ==============================================================================
# Academic Sub-weights (Within Academic Category = 1.00)
ACADEMIC_SUB_WEIGHTS = {
    "cgpa": 0.50,           # Scaled from 10.0 scale to 100.0 (CGPA * 10)
    "avg_marks": 0.30,      # Average subject marks (0-100 scale)
    "backlog_penalty": 0.20 # 100 - (backlogs * 25), min 0
}

# LMS Sub-weights (Within LMS Category = 1.00)
LMS_SUB_WEIGHTS = {
    "login_frequency": 0.40,      # Benchmark: 50 logins/month = 100%
    "assignment_completion": 0.60 # Already 0-100%
}
LMS_LOGIN_BENCHMARK = 50.0

# Engagement Sub-weights (Within Engagement Category = 1.00)
ENGAGEMENT_SUB_WEIGHTS = {
    "events": 0.20,         # Benchmark: 8 events = 100%
    "clubs": 0.25,          # Benchmark: 3 clubs = 100%
    "hackathons": 0.30,     # Benchmark: 4 hackathons = 100%
    "certifications": 0.15, # Benchmark: 3 certifications = 100%
    "tier": 0.10            # "High": 100, "Medium": 75, "Low": 40
}
ENGAGEMENT_BENCHMARKS = {
    "events_max": 8.0,
    "clubs_max": 3.0,
    "hackathons_max": 4.0,
    "certifications_max": 3.0,
    "tier_map": {"High": 100.0, "Medium": 75.0, "Low": 40.0}
}

# Placement Sub-weights (Baseline when all 3 present)
PLACEMENT_SUB_WEIGHTS = {
    "aptitude": 0.30,
    "coding": 0.40,
    "mock_interview": 0.30
}

# Skills Sub-weights (Baseline when both present)
SKILLS_SUB_WEIGHTS = {
    "technical": 0.60,
    "soft": 0.40
}

# Feedback Sub-weights (Baseline when both present, 1.0-5.0 scale -> normalized to 0-100)
FEEDBACK_SUB_WEIGHTS = {
    "faculty": 0.60,
    "student_satisfaction": 0.40
}

# ==============================================================================
# 3. RISK CLASSIFICATION THRESHOLDS
# ==============================================================================
# Academic Risk Thresholds
ACADEMIC_RISK_THRESHOLDS = {
    "cgpa_critical": 5.50,
    "cgpa_moderate": 7.00,
    "backlog_critical": 2,
    "backlog_moderate": 1,
    "attendance_critical": 65.0,
    "attendance_moderate": 75.0,
    "assignment_critical": 50.0,
    "assignment_moderate": 70.0,
    "subject_fail_mark": 40.0
}

# Placement Risk Thresholds
PLACEMENT_RISK_THRESHOLDS = {
    "readiness_critical": 50.0,
    "readiness_moderate": 70.0,
    "coding_critical": 50.0,
    "coding_moderate": 65.0,
    "aptitude_critical": 50.0,
    "aptitude_moderate": 65.0,
    "mock_critical": 50.0,
    "mock_moderate": 65.0,
    "technical_critical": 55.0,
    "technical_moderate": 70.0
}

# ==============================================================================
# 4. STUDENT SEGMENTATION BOUNDARIES
# ==============================================================================
SEGMENT_THRESHOLDS = {
    "high_academic_cutoff": 75.0,
    "low_academic_cutoff": 65.0,
    "high_placement_cutoff": 75.0,
    "low_placement_cutoff": 65.0,
}

# ==============================================================================
# 5. DATA DIRECTORIES
# ==============================================================================
DEFAULT_DATA_DIR = "data"
DEFAULT_PROCESSED_DIR = "data/processed"
