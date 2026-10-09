"""
test_integration.py
Tests data loading, relationship validation, duplicate detection, and multi-table integration.
"""

import pytest
import pandas as pd
import numpy as np

from src.data_loader import DataLoader
from src.integrator import DataIntegrator

def test_data_loader_loads_all_files():
    loader = DataLoader(data_dir="data")
    raw_data = loader.load_all()
    assert len(raw_data) == 8
    assert "students" in raw_data
    assert "academic" in raw_data
    assert "attendance" in raw_data

    audit = loader.get_audit_summary()
    assert audit["master_student_count"] == 120
    assert audit["referential_integrity_valid"] is True

def test_data_loader_detects_orphan_student_ids():
    loader = DataLoader(data_dir="data")
    raw_data = loader.load_all()

    # Artificially inject an orphan record in placement
    corrupted_placement = raw_data["placement"].copy()
    corrupted_placement.loc[0, "student_id"] = "STU9999_ORPHAN"
    loader.raw_data["placement"] = corrupted_placement

    with pytest.raises(ValueError, match="Referential integrity violation"):
        loader._validate_relationships()

def test_integrator_aggregates_without_double_counting():
    loader = DataLoader(data_dir="data")
    raw_data = loader.load_all()

    integrator = DataIntegrator(raw_data)
    unified_df = integrator.integrate()

    # Exactly 120 students; no Cartesian expansion
    assert len(unified_df) == 120
    assert unified_df["student_id"].nunique() == 120

    # Verify academic aggregation on first student
    s1_id = unified_df.iloc[0]["student_id"]
    s1_subjects = raw_data["academic"][raw_data["academic"]["student_id"] == s1_id]
    expected_avg = round(float(s1_subjects["subject_marks"].mean()), 2)
    assert abs(unified_df.iloc[0]["academic_avg_marks"] - expected_avg) < 1e-2

    # Verify attendance aggregation on first student
    s1_att = raw_data["attendance"][raw_data["attendance"]["student_id"] == s1_id]
    tot_att = int(s1_att["classes_attended"].sum())
    tot_sch = int(s1_att["total_classes"].sum())
    expected_att_pct = round((tot_att / tot_sch) * 100.0, 2)
    assert abs(unified_df.iloc[0]["overall_attendance_percentage"] - expected_att_pct) < 1e-2

def test_integrator_preserves_detailed_breakdowns():
    loader = DataLoader(data_dir="data")
    raw_data = loader.load_all()

    integrator = DataIntegrator(raw_data)
    integrator.integrate()
    profiles = integrator.get_detailed_profiles()

    assert len(profiles) == 120
    sample_profile = profiles["STU1001"]
    assert "subject_breakdown" in sample_profile
    assert len(sample_profile["subject_breakdown"]) == 4
    assert "attendance_breakdown" in sample_profile
    assert len(sample_profile["attendance_breakdown"]) == 4
