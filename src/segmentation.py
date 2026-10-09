"""
segmentation.py
Data-driven, explainable student segmentation module for Smart Campus Analytics Phase 2.
Classifies students into actionable personas based on Academic and Placement performance indices.
"""

from typing import Dict, Any, Tuple
import pandas as pd
from src.config import SEGMENT_THRESHOLDS

class StudentSegmenter:
    def __init__(self, thresholds: Dict[str, float] = None):
        self.th = thresholds or SEGMENT_THRESHOLDS

    def assign_segment(self, row: pd.Series) -> Dict[str, str]:
        """Classifies a student into a distinct performance segment with explanation."""
        acad = float(row.get("academic_score", 0.0))
        place = float(row.get("placement_score", 0.0))

        high_acad = acad >= self.th["high_academic_cutoff"]
        low_acad = acad < self.th["low_academic_cutoff"]

        high_place = place >= self.th["high_placement_cutoff"]
        low_place = place < self.th["low_placement_cutoff"]

        # Classification Matrix
        if high_acad and high_place:
            name = "Strong Academics, Strong Placement Readiness"
            desc = "Top-tier student excelling in theoretical coursework, exams, and technical recruitment readiness."
            strategy = "Honors mentorship, advanced leadership opportunities, product hackathons, and tier-1 campus placements."

        elif high_acad and low_place:
            name = "Strong Academics, Low Placement Readiness"
            desc = "High academic achiever who is struggling with competitive coding, aptitude tests, or interview rounds."
            strategy = "Intensive placement bootcamp, coding problem sets, and behavioral/mock interview coaching."

        elif low_acad and high_place:
            name = "Weak Academics, Strong Placement Readiness"
            desc = "Hands-on problem solver/hacker with competitive coding skills but slipping in university grades or backlogs."
            strategy = "Academic counseling, remedial coursework prep to clear backlogs, and attendance recovery."

        elif low_acad and low_place:
            name = "Needs Improvement in Multiple Areas"
            desc = "Student facing critical challenges across coursework, attendance, and recruitment preparedness."
            strategy = "Holistic academic advisory, weekly faculty mentor check-ins, study groups, and foundational skill workshops."

        elif low_acad and not low_place:
            name = "Needs Academic Improvement"
            desc = "Moderate placement skills but vulnerable academic standing (low CGPA or backlogs)."
            strategy = "Prioritize academic stabilization, mandatory faculty tutoring, and assignment completion."

        elif not low_acad and low_place:
            name = "Needs Placement Preparation"
            desc = "Steady academic foundation but underprepared for competitive placement assessments."
            strategy = "Enroll in structured placement training modules, aptitude test series, and resume building."

        elif high_acad and not high_place:
            name = "Strong Academics, Moderate Placement Readiness"
            desc = "High GPA student with solid fundamentals approaching recruitment qualification standards."
            strategy = "Fine-tune advanced algorithmic coding and participate in company-specific mock tests."

        elif not high_acad and high_place:
            name = "Moderate Academics, Strong Placement Readiness"
            desc = "Solid coursework performer with distinguished technical coding competencies."
            strategy = "Maintain academic momentum while targeting high-package campus placement opportunities."

        else:
            name = "Consistent All-Rounder"
            desc = "Balanced, dependable performer maintaining steady grades and respectable placement readiness."
            strategy = "Targeted skill specializations, industry certifications, and leadership roles."

        return {
            "segment_name": name,
            "segment_description": desc,
            "focus_strategy": strategy
        }

    def add_segment_columns_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Appends segment assignments to the unified DataFrame."""
        df_out = df.copy()
        names = []
        descriptions = []
        strategies = []

        for _, row in df_out.iterrows():
            res = self.assign_segment(row)
            names.append(res["segment_name"])
            descriptions.append(res["segment_description"])
            strategies.append(res["focus_strategy"])

        df_out["student_segment"] = names
        df_out["segment_description"] = descriptions
        df_out["segment_focus_strategy"] = strategies

        return df_out
