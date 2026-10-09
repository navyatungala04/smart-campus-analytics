"""
integrator.py
Dataset integration module for Smart Campus Analytics Phase 2.
Aggregates subject-level academics and attendance without double-counting students,
and merges all seven data categories into a unified student profile.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

class DataIntegrator:
    def __init__(self, raw_data: Dict[str, pd.DataFrame]):
        self.raw_data = raw_data
        self.unified_df: pd.DataFrame = pd.DataFrame()
        self.detailed_profiles: Dict[str, Dict[str, Any]] = {}

    def integrate(self) -> pd.DataFrame:
        """Combines all 7 categories into a single unified student DataFrame."""
        df_students = self.raw_data["students"].copy()
        df_academic = self.raw_data["academic"].copy()
        df_attendance = self.raw_data["attendance"].copy()
        df_lms = self.raw_data["lms_activity"].copy()
        df_engagement = self.raw_data["engagement"].copy()
        df_placement = self.raw_data["placement"].copy()
        df_skills = self.raw_data["skills"].copy()
        df_feedback = self.raw_data["feedback"].copy()

        # 1. Aggregate Academic records per student
        # Prevent double-counting: compute summary metrics at the student level
        academic_agg = df_academic.groupby("student_id").agg(
            cgpa=("cgpa", "first"),
            backlogs=("backlogs", "first"),
            academic_avg_marks=("subject_marks", lambda s: round(float(s.mean()), 2)),
            academic_min_marks=("subject_marks", lambda s: round(float(s.min()), 2)),
            academic_max_marks=("subject_marks", lambda s: round(float(s.max()), 2)),
            subjects_enrolled_count=("subject_name", "count"),
            failed_subjects_count=("subject_marks", lambda s: int((s < 40.0).sum()))
        ).reset_index()

        # Subject-level breakdowns preserved for fine-grained reporting
        subject_breakdown_map: Dict[str, List[Dict[str, Any]]] = {}
        for s_id, group in df_academic.groupby("student_id"):
            subject_breakdown_map[s_id] = [
                {
                    "subject_name": row["subject_name"],
                    "marks": float(row["subject_marks"]),
                    "passed": bool(row["subject_marks"] >= 40.0)
                }
                for _, row in group.iterrows()
            ]

        # 2. Aggregate Attendance records per student
        attendance_agg = df_attendance.groupby("student_id").agg(
            total_classes_attended=("classes_attended", "sum"),
            total_classes_scheduled=("total_classes", "sum"),
            min_subject_attendance_percentage=("attendance_percentage", lambda s: round(float(s.min()), 2)),
            low_attendance_subjects_count=("attendance_percentage", lambda s: int((s < 75.0).sum()))
        ).reset_index()

        # Recalculate true cumulative attendance percentage
        attendance_agg["overall_attendance_percentage"] = np.round(
            (attendance_agg["total_classes_attended"] / attendance_agg["total_classes_scheduled"]) * 100.0, 2
        )

        attendance_breakdown_map: Dict[str, List[Dict[str, Any]]] = {}
        for s_id, group in df_attendance.groupby("student_id"):
            attendance_breakdown_map[s_id] = [
                {
                    "subject_name": row["subject_name"],
                    "classes_attended": int(row["classes_attended"]),
                    "total_classes": int(row["total_classes"]),
                    "attendance_percentage": float(row["attendance_percentage"]),
                    "is_below_75": bool(row["attendance_percentage"] < 75.0)
                }
                for _, row in group.iterrows()
            ]

        # 3. Merge all tables onto the students master DataFrame
        # 1-to-1 merge maintains exactly len(df_students) rows
        merged = df_students.merge(academic_agg, on="student_id", how="left")
        merged = merged.merge(attendance_agg, on="student_id", how="left")
        merged = merged.merge(df_lms, on="student_id", how="left")
        merged = merged.merge(df_engagement, on="student_id", how="left")
        merged = merged.merge(df_placement, on="student_id", how="left")
        merged = merged.merge(df_skills, on="student_id", how="left")
        merged = merged.merge(df_feedback, on="student_id", how="left")

        # Validate that no student row was lost or multiplied
        if len(merged) != len(df_students):
            raise ValueError(
                f"Row mismatch during integration: Expected {len(df_students)} rows, got {len(merged)} rows. "
                "Check for Cartesian product expansion."
            )

        self.unified_df = merged

        # Build detailed rich object profile for each student
        for _, row in merged.iterrows():
            s_id = row["student_id"]
            self.detailed_profiles[s_id] = {
                **row.to_dict(),
                "subject_breakdown": subject_breakdown_map.get(s_id, []),
                "attendance_breakdown": attendance_breakdown_map.get(s_id, [])
            }

        return self.unified_df

    def get_unified_dataframe(self) -> pd.DataFrame:
        """Returns the integrated flat DataFrame."""
        return self.unified_df

    def get_detailed_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Returns student profiles with nested subject and attendance breakdowns."""
        return self.detailed_profiles
