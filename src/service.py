"""
service.py
Unified Backend-Ready Service Facade for Smart Campus Analytics Phase 2.
Coordinates data loading, integration, success scoring, risk assessment,
segmentation, and recommendation generation. Ready for FastAPI route binding.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from src.config import DEFAULT_DATA_DIR, DEFAULT_PROCESSED_DIR
from src.data_loader import DataLoader
from src.integrator import DataIntegrator
from src.scoring import StudentSuccessScorer
from src.risk_analyzer import RiskAnalyzer
from src.segmentation import StudentSegmenter
from src.recommendations import RecommendationEngine

def _clean_nans(val: Any) -> Any:
    """Recursively replaces NaN/inf floats with None for valid JSON serialization."""
    if isinstance(val, float):
        if np.isnan(val) or np.isinf(val):
            return None
        return round(val, 2)
    elif isinstance(val, dict):
        return {k: _clean_nans(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [_clean_nans(x) for x in val]
    return val

class AnalyticsService:
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.loader = DataLoader(data_dir=data_dir)
        self.scorer = StudentSuccessScorer()
        self.risk_analyzer = RiskAnalyzer()
        self.segmenter = StudentSegmenter()
        self.recommender = RecommendationEngine()
        
        self.raw_data: Dict[str, pd.DataFrame] = {}
        self.processed_df: pd.DataFrame = pd.DataFrame()
        self.student_dossiers: Dict[str, Dict[str, Any]] = {}
        self.is_initialized = False

    def apply_persisted_updates(self, auth_db_instance: Optional[Any] = None) -> None:
        """Applies persistent academic marks and attendance overrides from SQLite without touching source CSVs."""
        try:
            from src.auth_db import AuthDatabase
            db = auth_db_instance or AuthDatabase()
            acad_updates = db.get_academic_updates()
            att_updates = db.get_attendance_updates()

            if acad_updates and "academic" in self.raw_data:
                df_acad = self.raw_data["academic"]
                for upd in acad_updates:
                    mask = (df_acad["student_id"] == upd["student_id"]) & (df_acad["subject_name"] == upd["subject_name"])
                    if mask.any():
                        df_acad.loc[mask, "subject_marks"] = float(upd["marks"])

            if att_updates and "attendance" in self.raw_data:
                df_att = self.raw_data["attendance"]
                for upd in att_updates:
                    mask = (df_att["student_id"] == upd["student_id"]) & (df_att["subject_name"] == upd["subject_name"])
                    if mask.any():
                        df_att.loc[mask, "classes_attended"] = int(upd["classes_attended"])
                        df_att.loc[mask, "total_classes"] = int(upd["total_classes"])
                        df_att.loc[mask, "attendance_percentage"] = float(upd["attendance_percentage"])
        except Exception as e:
            # Tolerant if database is initializing
            pass

    def _rebuild_pipeline(self) -> None:
        """Executes integration, scoring, risk analysis, segmentation, and dossier creation."""
        # 1. Integrate multi-table records without double counting
        integrator = DataIntegrator(self.raw_data)
        integrated_df = integrator.integrate()
        detailed_profiles = integrator.get_detailed_profiles()

        # 2. Compute Student Success Score & components
        scored_df = self.scorer.compute_scores(integrated_df)

        # 3. Assess Academic and Placement Risks
        risked_df = self.risk_analyzer.add_risk_columns_to_df(scored_df)

        # 4. Assign Segment Categories
        final_df = self.segmenter.add_segment_columns_to_df(risked_df)
        self.processed_df = final_df

        # 5. Build individual rich student dossiers (backend/API ready)
        self.student_dossiers = {}
        for _, row in final_df.iterrows():
            s_id = row["student_id"]
            score_breakdown = self.scorer.get_score_breakdown(row)
            risk_assessment = self.risk_analyzer.assess_student_risks(row)
            segment_info = self.segmenter.assign_segment(row)
            recommendations = self.recommender.generate_recommendations(row)
            
            raw_dossier = {
                "student_id": s_id,
                "personal_info": {
                    "student_name": row["student_name"],
                    "department": row["department"],
                    "academic_year": row["academic_year"],
                    "semester": int(row["semester"]),
                    "email": row["email"]
                },
                "success_score": {
                    "overall_score": float(row["student_success_score"]),
                    "breakdown": score_breakdown
                },
                "risk_analysis": risk_assessment,
                "segmentation": segment_info,
                "recommendations": recommendations,
                "academic_details": {
                    "cgpa": float(row["cgpa"]),
                    "backlogs": int(row["backlogs"]),
                    "average_marks": float(row["academic_avg_marks"]),
                    "min_marks": float(row["academic_min_marks"]),
                    "max_marks": float(row["academic_max_marks"]),
                    "subjects_breakdown": detailed_profiles.get(s_id, {}).get("subject_breakdown", [])
                },
                "attendance_details": {
                    "overall_percentage": float(row["overall_attendance_percentage"]),
                    "classes_attended": int(row["total_classes_attended"]),
                    "classes_scheduled": int(row["total_classes_scheduled"]),
                    "low_attendance_subjects": int(row["low_attendance_subjects_count"]),
                    "attendance_breakdown": detailed_profiles.get(s_id, {}).get("attendance_breakdown", [])
                },
                "lms_details": {
                    "login_frequency": int(row["login_frequency"]),
                    "assignments_completed": int(row["assignments_completed"]),
                    "total_assignments": int(row["total_assignments"]),
                    "assignment_completion_percentage": float(row["assignment_completion_percentage"])
                },
                "engagement_details": {
                    "events_attended": int(row["events_attended"]),
                    "clubs_participated": int(row["clubs_participated"]),
                    "hackathons_participated": int(row["hackathons_participated"]),
                    "extracurricular_tier": row["extracurricular_participation"],
                    "certifications_count": int(row["certifications_count"])
                },
                "placement_details": {
                    "aptitude_score": float(row["aptitude_score"]),
                    "coding_score": float(row["coding_score"]),
                    "mock_interview_score": row["mock_interview_score"],
                    "placement_readiness_score": float(row["placement_score"]),
                    "mock_interview_pending": bool(row["mock_interview_pending"])
                },
                "skills_details": {
                    "technical_skill_score": float(row["technical_skill_score"]),
                    "soft_skill_score": row["soft_skill_score"],
                    "assessed_skills": row["assessed_skills"],
                    "assessment_date": row["assessment_date"],
                    "soft_skill_pending": bool(row["soft_skill_pending"])
                },
                "feedback_details": {
                    "faculty_feedback_score": float(row["faculty_feedback_score"]),
                    "student_satisfaction_score": row["student_satisfaction_score"],
                    "feedback_date": row["feedback_date"],
                    "satisfaction_survey_pending": bool(row["satisfaction_survey_pending"])
                }
            }
            # Clean all NaNs for clean JSON output
            self.student_dossiers[s_id] = _clean_nans(raw_dossier)

        self.is_initialized = True

    def initialize(self, auth_db_instance: Optional[Any] = None) -> None:
        """Executes full data ingestion, scoring, and analysis pipeline."""
        # 1. Load raw data
        self.raw_data = self.loader.load_all()

        # 2. Apply persistent overrides from SQLite
        self.apply_persisted_updates(auth_db_instance)

        # 3. Build analytical pipeline
        self._rebuild_pipeline()

    def reload(self, auth_db_instance: Optional[Any] = None) -> None:
        """Reloads raw data and persistent SQLite updates, rebuilding the pipeline."""
        self.initialize(auth_db_instance)

    def update_student_records(
        self,
        student_id: str,
        academic_updates: Optional[List[Dict[str, Any]]] = None,
        attendance_updates: Optional[List[Dict[str, Any]]] = None,
        auth_db_instance: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Persistently updates marks and attendance for a student,
        recalculates all analytics, and returns the updated student dossier.
        """
        clean_id = student_id.strip().upper()
        if not self.is_initialized:
            self.initialize(auth_db_instance)

        if clean_id not in self.student_dossiers:
            raise ValueError(f"Student ID '{student_id}' not found in active cohort.")

        from src.auth_db import AuthDatabase
        db = auth_db_instance or AuthDatabase()

        # 1. Validation and persistence in SQLite
        if academic_updates:
            for item in academic_updates:
                subj = str(item["subject_name"]).strip()
                marks = float(item["marks"])
                if marks < 0.0 or marks > 100.0:
                    raise ValueError(f"Marks for '{subj}' must be between 0.0 and 100.0 (got {marks}).")
                db.save_academic_update(clean_id, subj, marks)

        if attendance_updates:
            for item in attendance_updates:
                subj = str(item["subject_name"]).strip()
                att = int(item["classes_attended"])
                tot = int(item["total_classes"])
                if tot <= 0:
                    raise ValueError(f"Total scheduled classes for '{subj}' must be greater than 0.")
                if att < 0:
                    raise ValueError(f"Attended classes for '{subj}' cannot be negative.")
                if att > tot:
                    raise ValueError(f"Attended classes ({att}) cannot exceed total classes ({tot}) for '{subj}'.")
                db.save_attendance_update(clean_id, subj, att, tot)

        # 2. Apply persisted overrides to in-memory DataFrames
        self.apply_persisted_updates(db)

        # 3. Re-run complete pipeline to recalculate scores, risks, segments, and recommendations
        self._rebuild_pipeline()

        return self.student_dossiers[clean_id]

    def get_processed_dataframe(self) -> pd.DataFrame:
        """Returns the fully processed master DataFrame."""
        if not self.is_initialized:
            self.initialize()
        return self.processed_df

    def get_all_student_profiles(self) -> List[Dict[str, Any]]:
        """Returns list of all rich student dossiers."""
        if not self.is_initialized:
            self.initialize()
        return list(self.student_dossiers.values())

    def get_student_profile(self, student_id: str, auth_db_instance: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """Retrieves comprehensive dossier for a specific student ID with persisted completion status."""
        if not self.is_initialized:
            self.initialize(auth_db_instance)
        clean_id = student_id.strip().upper()
        dossier = self.student_dossiers.get(clean_id)
        if not dossier:
            return None

        # Enrich recommendations with persisted completion statuses from SQLite
        dossier_copy = dict(dossier)
        try:
            from src.auth_db import AuthDatabase
            db = auth_db_instance or AuthDatabase()
            completions = db.get_recommendation_completions(clean_id)
            recs = dossier_copy.get("recommendations", [])
            enriched_recs = []
            for r in recs:
                rec_dict = dict(r)
                rec_id = rec_dict.get("id") or f"rec_{rec_dict.get('related_metric', 'task')}"
                rec_dict["id"] = rec_id
                comp = completions.get(rec_id, {})
                rec_dict["is_completed"] = comp.get("status") == "completed"
                rec_dict["status"] = comp.get("status", "pending")
                rec_dict["completed_at"] = comp.get("completed_at")
                enriched_recs.append(rec_dict)
            dossier_copy["recommendations"] = enriched_recs
        except Exception:
            pass

        return dossier_copy

    def get_student_improvement_plan(self, student_id: str, auth_db_instance: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves consolidated improvement plan for student:
        - System recommendations with persistent completion status
        - Custom student-created plans
        - Real-time aggregated statistics (total, completed, pending, overdue, completion percentage)
        """
        clean_id = student_id.strip().upper()
        profile = self.get_student_profile(clean_id, auth_db_instance)
        if not profile:
            return None

        try:
            from src.auth_db import AuthDatabase
            db = auth_db_instance or AuthDatabase()
            custom_plans = db.get_custom_plans(clean_id)
        except Exception:
            custom_plans = []

        system_recs = profile.get("recommendations", [])
        today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Counts
        sys_total = len(system_recs)
        sys_completed = sum(1 for r in system_recs if r.get("is_completed"))

        custom_total = len(custom_plans)
        custom_completed = sum(1 for p in custom_plans if p.get("status") == "completed")

        # Overdue tasks (tasks with target_date < today and not completed)
        overdue_count = 0
        for p in custom_plans:
            if p.get("status") != "completed" and p.get("target_date"):
                # Safe date comparison
                t_date = str(p["target_date"])[:10]
                if t_date < today_iso:
                    overdue_count += 1

        total_tasks = sys_total + custom_total
        completed_tasks = sys_completed + custom_completed
        pending_tasks = total_tasks - completed_tasks
        completion_pct = round((completed_tasks / total_tasks * 100.0), 1) if total_tasks > 0 else 0.0

        return {
            "student_id": clean_id,
            "system_recommendations": system_recs,
            "custom_plans": custom_plans,
            "stats": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "overdue_tasks": overdue_count,
                "completion_percentage": completion_pct,
                "system_total": sys_total,
                "system_completed": sys_completed,
                "custom_total": custom_total,
                "custom_completed": custom_completed,
            }
        }

    def get_cohort_summary(self) -> Dict[str, Any]:
        """Calculates cohort-wide analytics and distribution metrics."""
        if not self.is_initialized:
            self.initialize()

        df = self.processed_df
        return {
            "total_students": len(df),
            "average_success_score": round(float(df["student_success_score"].mean()), 2),
            "median_success_score": round(float(df["student_success_score"].median()), 2),
            "score_quartiles": {
                "q25": round(float(df["student_success_score"].quantile(0.25)), 2),
                "q75": round(float(df["student_success_score"].quantile(0.75)), 2)
            },
            "academic_risk_distribution": df["academic_risk_level"].value_counts().to_dict(),
            "placement_risk_distribution": df["placement_risk_level"].value_counts().to_dict(),
            "segment_distribution": df["student_segment"].value_counts().to_dict(),
            "department_breakdown": df.groupby("department")["student_success_score"].mean().round(2).to_dict()
        }

    def export_processed_data(self, output_dir: str = DEFAULT_PROCESSED_DIR) -> Dict[str, str]:
        """Saves all processed analytics to CSV and JSON formats."""
        if not self.is_initialized:
            self.initialize()

        os.makedirs(output_dir, exist_ok=True)
        paths = {}

        # 1. Master unified profile CSV
        unified_csv = os.path.join(output_dir, "unified_student_profiles.csv")
        self.processed_df.to_csv(unified_csv, index=False)
        paths["unified_profiles_csv"] = unified_csv

        # 2. Risk assessments CSV
        risk_cols = [
            "student_id", "student_name", "department", "academic_risk_level",
            "academic_risk_triggers_count", "placement_risk_level",
            "placement_risk_triggers_count", "overall_risk_summary"
        ]
        risk_csv = os.path.join(output_dir, "student_risk_assessments.csv")
        self.processed_df[risk_cols].to_csv(risk_csv, index=False)
        paths["risk_assessments_csv"] = risk_csv

        # 3. Student recommendations CSV (flattened)
        rec_rows = []
        for s_id, dossier in self.student_dossiers.items():
            for rec in dossier["recommendations"]:
                rec_rows.append({
                    "student_id": s_id,
                    "student_name": dossier["personal_info"]["student_name"],
                    "category": rec["category"],
                    "priority": rec["priority"],
                    "related_metric": rec["related_metric"],
                    "current_value": rec["current_value"],
                    "improvement_target": rec["improvement_target"],
                    "reason": rec["reason"],
                    "suggested_action": rec["suggested_action"]
                })
        rec_df = pd.DataFrame(rec_rows)
        rec_csv = os.path.join(output_dir, "student_recommendations.csv")
        rec_df.to_csv(rec_csv, index=False)
        paths["recommendations_csv"] = rec_csv

        # 4. Master JSON file for fast frontend/API responses
        master_json = os.path.join(output_dir, "unified_analytics_master.json")
        with open(master_json, "w", encoding="utf-8") as f:
            json.dump({
                "cohort_summary": self.get_cohort_summary(),
                "students": self.student_dossiers
            }, f, indent=2)
        paths["master_json"] = master_json

        return paths
