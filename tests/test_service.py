"""
test_service.py
Tests AnalyticsService facade, invalid student IDs, cohort summaries, and exports.
"""

import os
import pytest

from src.service import AnalyticsService

@pytest.fixture(scope="module")
def initialized_service():
    service = AnalyticsService(data_dir="data")
    service.initialize()
    return service

def test_service_initialization(initialized_service):
    assert initialized_service.is_initialized is True
    assert len(initialized_service.student_dossiers) == 120

def test_get_valid_student_profile(initialized_service):
    dossier = initialized_service.get_student_profile("STU1001")
    assert dossier is not None
    assert dossier["student_id"] == "STU1001"
    assert "personal_info" in dossier
    assert "success_score" in dossier
    assert "risk_analysis" in dossier
    assert "segmentation" in dossier
    assert "recommendations" in dossier
    assert len(dossier["recommendations"]) > 0

def test_get_invalid_student_id_returns_none(initialized_service):
    dossier = initialized_service.get_student_profile("NON_EXISTENT_ID_9999")
    assert dossier is None

def test_cohort_summary_structure(initialized_service):
    summary = initialized_service.get_cohort_summary()
    assert summary["total_students"] == 120
    assert 0 <= summary["average_success_score"] <= 100
    assert "academic_risk_distribution" in summary
    assert "placement_risk_distribution" in summary
    assert "segment_distribution" in summary

def test_export_processed_data(initialized_service, tmp_path):
    out_dir = str(tmp_path / "processed_test")
    paths = initialized_service.export_processed_data(output_dir=out_dir)
    assert os.path.exists(paths["unified_profiles_csv"])
    assert os.path.exists(paths["risk_assessments_csv"])
    assert os.path.exists(paths["recommendations_csv"])
    assert os.path.exists(paths["master_json"])
