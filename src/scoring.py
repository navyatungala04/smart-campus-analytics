"""
scoring.py
Student Success Score calculation engine for Smart Campus Analytics Phase 2.
Normalizes all indicators to a 0-100 scale, applies transparent category weights,
handles missing data through re-weighting without punitive zero-scores,
and produces explainable component breakdowns.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from src.config import (
    CATEGORY_WEIGHTS,
    ACADEMIC_SUB_WEIGHTS,
    LMS_SUB_WEIGHTS,
    LMS_LOGIN_BENCHMARK,
    ENGAGEMENT_SUB_WEIGHTS,
    ENGAGEMENT_BENCHMARKS,
    PLACEMENT_SUB_WEIGHTS,
    SKILLS_SUB_WEIGHTS,
    FEEDBACK_SUB_WEIGHTS
)

class StudentSuccessScorer:
    def __init__(self, category_weights: Dict[str, float] = None):
        self.weights = category_weights or CATEGORY_WEIGHTS
        # Assert weights sum to 1.0
        assert abs(sum(self.weights.values()) - 1.0) < 1e-6, "Weights must sum to 1.0"

    def compute_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates normalized component scores and the final Student Success Score."""
        df_scored = df.copy()

        # 1. Academic Score (0-100)
        # Scaled CGPA (10 scale -> 100 scale)
        cgpa_scaled = np.clip(df_scored["cgpa"] * 10.0, 0.0, 100.0)
        marks_score = np.clip(df_scored["academic_avg_marks"], 0.0, 100.0)
        # Backlog penalty: 0 backlogs = 100, 1 = 75, 2 = 50, 3 = 25, 4+ = 0
        backlog_score = np.clip(100.0 - (df_scored["backlogs"] * 25.0), 0.0, 100.0)

        df_scored["academic_score"] = np.round(
            ACADEMIC_SUB_WEIGHTS["cgpa"] * cgpa_scaled +
            ACADEMIC_SUB_WEIGHTS["avg_marks"] * marks_score +
            ACADEMIC_SUB_WEIGHTS["backlog_penalty"] * backlog_score, 2
        )

        # 2. Attendance Score (0-100)
        df_scored["attendance_score"] = np.round(
            np.clip(df_scored["overall_attendance_percentage"], 0.0, 100.0), 2
        )

        # 3. LMS Activity Score (0-100)
        login_score = np.clip(
            (df_scored["login_frequency"] / LMS_LOGIN_BENCHMARK) * 100.0, 0.0, 100.0
        )
        assign_score = np.clip(df_scored["assignment_completion_percentage"], 0.0, 100.0)
        df_scored["lms_score"] = np.round(
            LMS_SUB_WEIGHTS["login_frequency"] * login_score +
            LMS_SUB_WEIGHTS["assignment_completion"] * assign_score, 2
        )

        # 4. Engagement Score (0-100)
        events_score = np.clip(
            (df_scored["events_attended"] / ENGAGEMENT_BENCHMARKS["events_max"]) * 100.0, 0.0, 100.0
        )
        clubs_score = np.clip(
            (df_scored["clubs_participated"] / ENGAGEMENT_BENCHMARKS["clubs_max"]) * 100.0, 0.0, 100.0
        )
        hackathons_score = np.clip(
            (df_scored["hackathons_participated"] / ENGAGEMENT_BENCHMARKS["hackathons_max"]) * 100.0, 0.0, 100.0
        )
        certs_score = np.clip(
            (df_scored["certifications_count"] / ENGAGEMENT_BENCHMARKS["certifications_max"]) * 100.0, 0.0, 100.0
        )
        tier_score = df_scored["extracurricular_participation"].map(
            ENGAGEMENT_BENCHMARKS["tier_map"]
        ).fillna(50.0)

        df_scored["engagement_score"] = np.round(
            ENGAGEMENT_SUB_WEIGHTS["events"] * events_score +
            ENGAGEMENT_SUB_WEIGHTS["clubs"] * clubs_score +
            ENGAGEMENT_SUB_WEIGHTS["hackathons"] * hackathons_score +
            ENGAGEMENT_SUB_WEIGHTS["certifications"] * certs_score +
            ENGAGEMENT_SUB_WEIGHTS["tier"] * tier_score, 2
        )

        # 5. Placement Readiness Score (0-100) with Missing Data Handling
        placement_scores = []
        mock_pending_flags = []
        for _, row in df_scored.iterrows():
            apt = float(row["aptitude_score"])
            cod = float(row["coding_score"])
            mock = row["mock_interview_score"]

            if pd.isna(mock):
                # Re-weight available components: 30% apt + 40% cod -> 3/7 and 4/7
                score = (3.0 / 7.0) * apt + (4.0 / 7.0) * cod
                mock_pending_flags.append(True)
            else:
                score = (
                    PLACEMENT_SUB_WEIGHTS["aptitude"] * apt +
                    PLACEMENT_SUB_WEIGHTS["coding"] * cod +
                    PLACEMENT_SUB_WEIGHTS["mock_interview"] * float(mock)
                )
                mock_pending_flags.append(False)
            placement_scores.append(round(min(100.0, max(0.0, score)), 2))

        df_scored["placement_score"] = placement_scores
        df_scored["mock_interview_pending"] = mock_pending_flags

        # 6. Technical & Soft Skills Score (0-100) with Missing Data Handling
        skills_scores = []
        soft_pending_flags = []
        for _, row in df_scored.iterrows():
            tech = float(row["technical_skill_score"])
            soft = row["soft_skill_score"]

            if pd.isna(soft):
                # Re-weight available technical skill component to 100%
                score = tech
                soft_pending_flags.append(True)
            else:
                score = (
                    SKILLS_SUB_WEIGHTS["technical"] * tech +
                    SKILLS_SUB_WEIGHTS["soft"] * float(soft)
                )
                soft_pending_flags.append(False)
            skills_scores.append(round(min(100.0, max(0.0, score)), 2))

        df_scored["skills_score"] = skills_scores
        df_scored["soft_skill_pending"] = soft_pending_flags

        # 7. Institutional Feedback Score (0-100) with Missing Data Handling
        feedback_scores = []
        sat_pending_flags = []
        for _, row in df_scored.iterrows():
            # Scale 1.0-5.0 to 0-100: (rating - 1.0) / 4.0 * 100.0
            fac_scaled = ((float(row["faculty_feedback_score"]) - 1.0) / 4.0) * 100.0
            sat = row["student_satisfaction_score"]

            if pd.isna(sat):
                # Re-weight available faculty mentorship component to 100%
                score = fac_scaled
                sat_pending_flags.append(True)
            else:
                sat_scaled = ((float(sat) - 1.0) / 4.0) * 100.0
                score = (
                    FEEDBACK_SUB_WEIGHTS["faculty"] * fac_scaled +
                    FEEDBACK_SUB_WEIGHTS["student_satisfaction"] * sat_scaled
                )
                sat_pending_flags.append(False)
            feedback_scores.append(round(min(100.0, max(0.0, score)), 2))

        df_scored["feedback_score"] = feedback_scores
        df_scored["satisfaction_survey_pending"] = sat_pending_flags

        # Composite Student Success Score (0-100)
        df_scored["student_success_score"] = np.round(
            self.weights["academic"] * df_scored["academic_score"] +
            self.weights["attendance"] * df_scored["attendance_score"] +
            self.weights["lms_activity"] * df_scored["lms_score"] +
            self.weights["engagement"] * df_scored["engagement_score"] +
            self.weights["placement"] * df_scored["placement_score"] +
            self.weights["skills"] * df_scored["skills_score"] +
            self.weights["feedback"] * df_scored["feedback_score"], 2
        )
        df_scored["student_success_score"] = np.clip(
            df_scored["student_success_score"], 0.0, 100.0
        )

        return df_scored

    def get_score_breakdown(self, student_row: pd.Series) -> Dict[str, Any]:
        """Produces a transparent breakdown of score components and their contributions."""
        return {
            "student_id": student_row["student_id"],
            "success_score": float(student_row["student_success_score"]),
            "components": {
                "academic": {
                    "raw_score": float(student_row["academic_score"]),
                    "weight": self.weights["academic"],
                    "contribution": round(float(student_row["academic_score"] * self.weights["academic"]), 2)
                },
                "attendance": {
                    "raw_score": float(student_row["attendance_score"]),
                    "weight": self.weights["attendance"],
                    "contribution": round(float(student_row["attendance_score"] * self.weights["attendance"]), 2)
                },
                "lms_activity": {
                    "raw_score": float(student_row["lms_score"]),
                    "weight": self.weights["lms_activity"],
                    "contribution": round(float(student_row["lms_score"] * self.weights["lms_activity"]), 2)
                },
                "engagement": {
                    "raw_score": float(student_row["engagement_score"]),
                    "weight": self.weights["engagement"],
                    "contribution": round(float(student_row["engagement_score"] * self.weights["engagement"]), 2)
                },
                "placement": {
                    "raw_score": float(student_row["placement_score"]),
                    "weight": self.weights["placement"],
                    "contribution": round(float(student_row["placement_score"] * self.weights["placement"]), 2),
                    "mock_interview_pending": bool(student_row.get("mock_interview_pending", False))
                },
                "skills": {
                    "raw_score": float(student_row["skills_score"]),
                    "weight": self.weights["skills"],
                    "contribution": round(float(student_row["skills_score"] * self.weights["skills"]), 2),
                    "soft_skill_pending": bool(student_row.get("soft_skill_pending", False))
                },
                "feedback": {
                    "raw_score": float(student_row["feedback_score"]),
                    "weight": self.weights["feedback"],
                    "contribution": round(float(student_row["feedback_score"] * self.weights["feedback"]), 2),
                    "satisfaction_survey_pending": bool(student_row.get("satisfaction_survey_pending", False))
                }
            }
        }
