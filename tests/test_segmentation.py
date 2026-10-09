"""
test_segmentation.py
Tests student segmentation assignments across multiple performance combinations.
"""

import pytest
import pandas as pd

from src.segmentation import StudentSegmenter

@pytest.fixture
def segmenter():
    return StudentSegmenter()

def test_segment_strong_strong(segmenter):
    row = pd.Series({"academic_score": 85.0, "placement_score": 88.0})
    seg = segmenter.assign_segment(row)
    assert seg["segment_name"] == "Strong Academics, Strong Placement Readiness"

def test_segment_strong_low_placement(segmenter):
    row = pd.Series({"academic_score": 85.0, "placement_score": 55.0})
    seg = segmenter.assign_segment(row)
    assert seg["segment_name"] == "Strong Academics, Low Placement Readiness"

def test_segment_weak_academics_strong_placement(segmenter):
    row = pd.Series({"academic_score": 58.0, "placement_score": 82.0})
    seg = segmenter.assign_segment(row)
    assert seg["segment_name"] == "Weak Academics, Strong Placement Readiness"

def test_segment_needs_multiple_areas(segmenter):
    row = pd.Series({"academic_score": 52.0, "placement_score": 45.0})
    seg = segmenter.assign_segment(row)
    assert seg["segment_name"] == "Needs Improvement in Multiple Areas"

def test_segment_needs_academic_improvement(segmenter):
    row = pd.Series({"academic_score": 60.0, "placement_score": 70.0})
    seg = segmenter.assign_segment(row)
    assert seg["segment_name"] == "Needs Academic Improvement"

def test_segment_needs_placement_prep(segmenter):
    row = pd.Series({"academic_score": 70.0, "placement_score": 60.0})
    seg = segmenter.assign_segment(row)
    assert seg["segment_name"] == "Needs Placement Preparation"

def test_segment_consistent_all_rounder(segmenter):
    row = pd.Series({"academic_score": 70.0, "placement_score": 70.0})
    seg = segmenter.assign_segment(row)
    assert seg["segment_name"] == "Consistent All-Rounder"
