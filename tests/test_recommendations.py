"""
test_recommendations.py
Tests personalized recommendation generation, metrics, priorities, targets, and reasons.
"""

import pytest
import pandas as pd
import numpy as np

from src.recommendations import RecommendationEngine

@pytest.fixture
def recommender():
    return RecommendationEngine()

def test_attendance_recommendation_and_consecutive_classes_calc(recommender):
    # Student with 60% attendance (30 attended out of 50 classes)
    mock_student = pd.Series({
        "student_id": "TEST_ATT",
        "overall_attendance_percentage": 60.0,
        "total_classes_attended": 30,
        "total_classes_scheduled": 50,
        "low_attendance_subjects_count": 2,
        "backlogs": 0,
        "assignment_completion_percentage": 90.0,
        "coding_score": 85.0,
        "aptitude_score": 85.0,
        "mock_interview_score": 85.0,
        "soft_skill_score": 85.0,
        "hackathons_participated": 1,
        "clubs_participated": 1,
        "certifications_count": 1
    })

    recs = recommender.generate_recommendations(mock_student)
    att_recs = [r for r in recs if r["category"] == "Attendance Recovery"]
    assert len(att_recs) == 1
    att_rec = att_recs[0]
    assert att_rec["priority"] == "Critical"
    assert "consecutive classes" in att_rec["improvement_target"]
    assert att_rec["related_metric"] == "overall_attendance_percentage"

def test_backlog_recommendation_critical_priority(recommender):
    mock_student = pd.Series({
        "student_id": "TEST_BL",
        "backlogs": 2,
        "overall_attendance_percentage": 85.0,
        "total_classes_attended": 42,
        "total_classes_scheduled": 50,
        "low_attendance_subjects_count": 0,
        "assignment_completion_percentage": 85.0,
        "coding_score": 80.0,
        "aptitude_score": 80.0,
        "mock_interview_score": 80.0,
        "soft_skill_score": 80.0,
        "hackathons_participated": 1,
        "clubs_participated": 1,
        "certifications_count": 1
    })

    recs = recommender.generate_recommendations(mock_student)
    bl_recs = [r for r in recs if r["category"] == "Academic Clearance"]
    assert len(bl_recs) == 1
    assert bl_recs[0]["priority"] == "Critical"
    assert "remedial coaching" in bl_recs[0]["suggested_action"]

def test_high_performer_receives_excellence_recommendation(recommender):
    mock_student = pd.Series({
        "student_id": "TEST_PERF",
        "backlogs": 0,
        "overall_attendance_percentage": 95.0,
        "total_classes_attended": 48,
        "total_classes_scheduled": 50,
        "low_attendance_subjects_count": 0,
        "assignment_completion_percentage": 100.0,
        "coding_score": 95.0,
        "aptitude_score": 92.0,
        "mock_interview_score": 90.0,
        "soft_skill_score": 90.0,
        "hackathons_participated": 3,
        "clubs_participated": 2,
        "certifications_count": 3,
        "student_success_score": 94.0
    })

    recs = recommender.generate_recommendations(mock_student)
    assert len(recs) >= 1
    categories = [r["category"] for r in recs]
    assert "Excellence & Leadership" in categories
