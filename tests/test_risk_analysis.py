"""
test_risk_analysis.py
Tests Academic and Placement risk classification logic, explainability, and pending data handling.
"""

import pytest
import pandas as pd
import numpy as np

from src.risk_analyzer import RiskAnalyzer

@pytest.fixture
def risk_analyzer():
    return RiskAnalyzer()

def test_academic_risk_high_triggers(risk_analyzer):
    # Student with 2 backlogs and low CGPA
    mock_student = pd.Series({
        "student_id": "TEST01",
        "cgpa": 4.80,
        "backlogs": 2,
        "overall_attendance_percentage": 58.0,
        "assignment_completion_percentage": 40.0,
        "academic_min_marks": 35.0,
        "failed_subjects_count": 1,
        "low_attendance_subjects_count": 3,
        "aptitude_score": 80.0,
        "coding_score": 80.0,
        "placement_score": 80.0,
        "technical_skill_score": 80.0,
        "mock_interview_score": 80.0,
        "soft_skill_score": 80.0
    })

    result = risk_analyzer.assess_student_risks(mock_student)
    assert result["academic_risk"]["level"] == "High"
    assert result["academic_risk"]["triggers_count"] >= 4
    indicators = [t["indicator"] for t in result["academic_risk"]["triggers"]]
    assert "Backlogs" in indicators
    assert "CGPA" in indicators
    assert "Overall Attendance" in indicators

def test_academic_risk_low_clean_record(risk_analyzer):
    mock_student = pd.Series({
        "student_id": "TEST02",
        "cgpa": 9.20,
        "backlogs": 0,
        "overall_attendance_percentage": 92.0,
        "assignment_completion_percentage": 100.0,
        "academic_min_marks": 85.0,
        "failed_subjects_count": 0,
        "low_attendance_subjects_count": 0,
        "aptitude_score": 90.0,
        "coding_score": 90.0,
        "placement_score": 90.0,
        "technical_skill_score": 90.0,
        "mock_interview_score": 90.0,
        "soft_skill_score": 90.0
    })

    result = risk_analyzer.assess_student_risks(mock_student)
    assert result["academic_risk"]["level"] == "Low"
    assert result["academic_risk"]["triggers_count"] == 0

def test_placement_risk_distinguishes_missing_mock(risk_analyzer):
    # Strong student but mock interview is missing (NaN)
    mock_student = pd.Series({
        "student_id": "TEST03",
        "cgpa": 8.50,
        "backlogs": 0,
        "overall_attendance_percentage": 88.0,
        "assignment_completion_percentage": 95.0,
        "academic_min_marks": 78.0,
        "failed_subjects_count": 0,
        "low_attendance_subjects_count": 0,
        "aptitude_score": 85.0,
        "coding_score": 85.0,
        "placement_score": 85.0,
        "technical_skill_score": 85.0,
        "mock_interview_score": np.nan,
        "soft_skill_score": 85.0
    })

    result = risk_analyzer.assess_student_risks(mock_student)
    # Missing mock should NOT trigger a high/moderate failure risk
    assert result["placement_risk"]["level"] == "Low"
    assert len(result["placement_risk"]["pending_assessments"]) > 0
    assert "Mock Interview assessment is pending" in result["placement_risk"]["pending_assessments"][0]

def test_placement_risk_high_triggers(risk_analyzer):
    mock_student = pd.Series({
        "student_id": "TEST04",
        "cgpa": 8.0,
        "backlogs": 0,
        "overall_attendance_percentage": 85.0,
        "assignment_completion_percentage": 85.0,
        "academic_min_marks": 70.0,
        "failed_subjects_count": 0,
        "low_attendance_subjects_count": 0,
        "aptitude_score": 38.0,
        "coding_score": 42.0,
        "placement_score": 40.0,
        "technical_skill_score": 45.0,
        "mock_interview_score": 40.0,
        "soft_skill_score": 45.0
    })

    result = risk_analyzer.assess_student_risks(mock_student)
    assert result["placement_risk"]["level"] == "High"
    assert result["placement_risk"]["triggers_count"] >= 3
