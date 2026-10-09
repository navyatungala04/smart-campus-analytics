"""
test_scoring.py
Tests Student Success Score weights, normalization bounds, missing data handling, and breakdowns.
"""

import pytest
import pandas as pd
import numpy as np

from src.config import CATEGORY_WEIGHTS
from src.data_loader import DataLoader
from src.integrator import DataIntegrator
from src.scoring import StudentSuccessScorer

@pytest.fixture
def scored_dataset():
    loader = DataLoader(data_dir="data")
    raw_data = loader.load_all()
    integrator = DataIntegrator(raw_data)
    unified_df = integrator.integrate()
    scorer = StudentSuccessScorer()
    return scorer.compute_scores(unified_df), scorer

def test_weights_sum_to_one():
    total_weight = sum(CATEGORY_WEIGHTS.values())
    assert abs(total_weight - 1.0) < 1e-6

def test_success_score_ranges(scored_dataset):
    df_scored, _ = scored_dataset
    score_cols = [
        "academic_score", "attendance_score", "lms_score", "engagement_score",
        "placement_score", "skills_score", "feedback_score", "student_success_score"
    ]
    for col in score_cols:
        assert (df_scored[col] >= 0.0).all(), f"{col} has negative values"
        assert (df_scored[col] <= 100.0).all(), f"{col} exceeds 100"

def test_missing_mock_interview_not_zero(scored_dataset):
    df_scored, _ = scored_dataset
    # Find students where mock_interview_score is NaN
    missing_mock_students = df_scored[df_scored["mock_interview_score"].isna()]
    assert len(missing_mock_students) > 0, "Expected students with missing mock interview"

    for _, row in missing_mock_students.iterrows():
        # Score must be non-zero (unless aptitude and coding are both 0)
        assert row["placement_score"] > 0
        assert row["mock_interview_pending"] is True
        # Verify formula: 3/7 * apt + 4/7 * cod
        expected = round((3.0 / 7.0) * row["aptitude_score"] + (4.0 / 7.0) * row["coding_score"], 2)
        assert abs(row["placement_score"] - expected) < 1e-2

def test_missing_soft_skill_not_zero(scored_dataset):
    df_scored, _ = scored_dataset
    missing_soft = df_scored[df_scored["soft_skill_score"].isna()]
    assert len(missing_soft) > 0

    for _, row in missing_soft.iterrows():
        assert row["soft_skill_pending"] is True
        assert abs(row["skills_score"] - row["technical_skill_score"]) < 1e-2

def test_score_breakdown_mathematical_consistency(scored_dataset):
    df_scored, scorer = scored_dataset
    sample_row = df_scored.iloc[0]
    breakdown = scorer.get_score_breakdown(sample_row)

    sum_contributions = sum(
        c["contribution"] for c in breakdown["components"].values()
    )
    # Contribution sum should match final score within rounding margin
    assert abs(sum_contributions - breakdown["success_score"]) < 0.2
