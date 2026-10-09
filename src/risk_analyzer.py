"""
risk_analyzer.py
Rule-based Academic and Placement risk analysis engine for Smart Campus Analytics Phase 2.
Evaluates clear indicators, severity tiers (High, Moderate, Low), explains triggered values,
and strictly distinguishes missing assessments from poor performance.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from src.config import ACADEMIC_RISK_THRESHOLDS, PLACEMENT_RISK_THRESHOLDS

class RiskAnalyzer:
    def __init__(self):
        self.acad_th = ACADEMIC_RISK_THRESHOLDS
        self.place_th = PLACEMENT_RISK_THRESHOLDS

    def assess_student_risks(self, student_row: pd.Series) -> Dict[str, Any]:
        """Performs comprehensive academic and placement risk assessments for a single student."""
        academic_assessment = self._evaluate_academic_risk(student_row)
        placement_assessment = self._evaluate_placement_risk(student_row)

        return {
            "student_id": student_row["student_id"],
            "academic_risk": academic_assessment,
            "placement_risk": placement_assessment,
            "overall_risk_summary": self._generate_overall_summary(
                academic_assessment["level"], placement_assessment["level"]
            )
        }

    def _evaluate_academic_risk(self, row: pd.Series) -> Dict[str, Any]:
        """Evaluates Academic Risk based on CGPA, backlogs, attendance, and assignment completion."""
        triggers: List[Dict[str, Any]] = []
        is_critical = False
        is_moderate = False

        cgpa = float(row["cgpa"])
        backlogs = int(row["backlogs"])
        att_pct = float(row["overall_attendance_percentage"])
        assign_pct = float(row["assignment_completion_percentage"])
        failed_subs = int(row.get("failed_subjects_count", 0))
        min_marks = float(row.get("academic_min_marks", 100.0))
        low_att_subs = int(row.get("low_attendance_subjects_count", 0))

        # 1. Backlogs check
        if backlogs >= self.acad_th["backlog_critical"]:
            is_critical = True
            triggers.append({
                "indicator": "Backlogs",
                "current_value": backlogs,
                "threshold": f">= {self.acad_th['backlog_critical']}",
                "severity": "Critical",
                "message": f"Student has {backlogs} active backlogs, jeopardizing degree progression and placement eligibility."
            })
        elif backlogs >= self.acad_th["backlog_moderate"]:
            is_moderate = True
            triggers.append({
                "indicator": "Backlogs",
                "current_value": backlogs,
                "threshold": f">= {self.acad_th['backlog_moderate']}",
                "severity": "Moderate",
                "message": f"Student has {backlogs} uncleared backlog requiring remedial clearance."
            })

        # 2. CGPA check
        if cgpa < self.acad_th["cgpa_critical"]:
            is_critical = True
            triggers.append({
                "indicator": "CGPA",
                "current_value": cgpa,
                "threshold": f"< {self.acad_th['cgpa_critical']}",
                "severity": "Critical",
                "message": f"Cumulative GPA ({cgpa:.2f}) is below the critical university standing threshold of {self.acad_th['cgpa_critical']}."
            })
        elif cgpa < self.acad_th["cgpa_moderate"]:
            is_moderate = True
            triggers.append({
                "indicator": "CGPA",
                "current_value": cgpa,
                "threshold": f"< {self.acad_th['cgpa_moderate']}",
                "severity": "Moderate",
                "message": f"Cumulative GPA ({cgpa:.2f}) is below target benchmark ({self.acad_th['cgpa_moderate']})."
            })

        # 3. Attendance check
        if att_pct < self.acad_th["attendance_critical"]:
            is_critical = True
            triggers.append({
                "indicator": "Overall Attendance",
                "current_value": f"{att_pct:.2f}%",
                "threshold": f"< {self.acad_th['attendance_critical']}%",
                "severity": "Critical",
                "message": f"Attendance is {att_pct:.2f}%, risking statutory exam debarment (< 65%)."
            })
        elif att_pct < self.acad_th["attendance_moderate"]:
            is_moderate = True
            triggers.append({
                "indicator": "Overall Attendance",
                "current_value": f"{att_pct:.2f}%",
                "threshold": f"< {self.acad_th['attendance_moderate']}%",
                "severity": "Moderate",
                "message": f"Attendance is {att_pct:.2f}%, falling below the mandatory 75% institutional requirement."
            })

        # 4. Assignment Completion
        if assign_pct < self.acad_th["assignment_critical"]:
            is_critical = True
            triggers.append({
                "indicator": "Assignment Completion",
                "current_value": f"{assign_pct:.2f}%",
                "threshold": f"< {self.acad_th['assignment_critical']}%",
                "severity": "Critical",
                "message": f"Only {assign_pct:.2f}% of LMS assignments submitted, reflecting severe disengagement."
            })
        elif assign_pct < self.acad_th["assignment_moderate"]:
            is_moderate = True
            triggers.append({
                "indicator": "Assignment Completion",
                "current_value": f"{assign_pct:.2f}%",
                "threshold": f"< {self.acad_th['assignment_moderate']}%",
                "severity": "Moderate",
                "message": f"Assignment completion ({assign_pct:.2f}%) is below optimal target (70%)."
            })

        # 5. Failed subjects / Low marks
        if failed_subs > 0:
            is_critical = True
            triggers.append({
                "indicator": "Failed Coursework",
                "current_value": f"{failed_subs} subject(s) with marks < 40",
                "threshold": "marks < 40",
                "severity": "Critical",
                "message": f"Failed coursework detected with minimum subject mark of {min_marks:.1f}."
            })

        # Determine level
        if is_critical:
            level = "High"
            explanation = "High Academic Risk: Critical concerns detected in core academic indicators (backlogs, low CGPA, or exam debarment attendance risk)."
        elif is_moderate:
            level = "Moderate"
            explanation = "Moderate Academic Risk: Borderline academic metrics identified; student requires targeted guidance to prevent escalation."
        else:
            level = "Low"
            explanation = "Low Academic Risk: Strong and consistent academic standing across CGPA, attendance, and coursework submissions."

        return {
            "level": level,
            "explanation": explanation,
            "triggers_count": len(triggers),
            "triggers": triggers
        }

    def _evaluate_placement_risk(self, row: pd.Series) -> Dict[str, Any]:
        """Evaluates Placement Risk based on aptitude, coding, mock interview, and technical skills."""
        triggers: List[Dict[str, Any]] = []
        pending_items: List[str] = []
        is_critical = False
        is_moderate = False

        apt = float(row["aptitude_score"])
        cod = float(row["coding_score"])
        readiness = float(row.get("placement_score", row.get("placement_readiness_score", 0.0)))
        tech_skill = float(row["technical_skill_score"])
        mock = row.get("mock_interview_score")
        soft = row.get("soft_skill_score")

        # 1. Placement Readiness
        if readiness < self.place_th["readiness_critical"]:
            is_critical = True
            triggers.append({
                "indicator": "Placement Readiness Score",
                "current_value": readiness,
                "threshold": f"< {self.place_th['readiness_critical']}",
                "severity": "Critical",
                "message": f"Overall placement readiness ({readiness:.1f}) is critically low for campus recruitment."
            })
        elif readiness < self.place_th["readiness_moderate"]:
            is_moderate = True
            triggers.append({
                "indicator": "Placement Readiness Score",
                "current_value": readiness,
                "threshold": f"< {self.place_th['readiness_moderate']}",
                "severity": "Moderate",
                "message": f"Placement readiness ({readiness:.1f}) is below competitive benchmark (70.0)."
            })

        # 2. Coding Assessment
        if cod < self.place_th["coding_critical"]:
            is_critical = True
            triggers.append({
                "indicator": "Coding Assessment",
                "current_value": cod,
                "threshold": f"< {self.place_th['coding_critical']}",
                "severity": "Critical",
                "message": f"Coding score ({cod:.1f}) is below basic programming qualification benchmark."
            })
        elif cod < self.place_th["coding_moderate"]:
            is_moderate = True
            triggers.append({
                "indicator": "Coding Assessment",
                "current_value": cod,
                "threshold": f"< {self.place_th['coding_moderate']}",
                "severity": "Moderate",
                "message": f"Coding score ({cod:.1f}) needs improvement for technical screening rounds."
            })

        # 3. Aptitude Assessment
        if apt < self.place_th["aptitude_critical"]:
            is_critical = True
            triggers.append({
                "indicator": "Aptitude Assessment",
                "current_value": apt,
                "threshold": f"< {self.place_th['aptitude_critical']}",
                "severity": "Critical",
                "message": f"Aptitude score ({apt:.1f}) fails standard corporate screening thresholds."
            })
        elif apt < self.place_th["aptitude_moderate"]:
            is_moderate = True
            triggers.append({
                "indicator": "Aptitude Assessment",
                "current_value": apt,
                "threshold": f"< {self.place_th['aptitude_moderate']}",
                "severity": "Moderate",
                "message": f"Aptitude score ({apt:.1f}) requires practice in quantitative & logical reasoning."
            })

        # 4. Technical Skills
        if tech_skill < self.place_th["technical_critical"]:
            is_critical = True
            triggers.append({
                "indicator": "Technical Domain Skills",
                "current_value": tech_skill,
                "threshold": f"< {self.place_th['technical_critical']}",
                "severity": "Critical",
                "message": f"Technical domain assessment ({tech_skill:.1f}) indicates major skill gaps."
            })
        elif tech_skill < self.place_th["technical_moderate"]:
            is_moderate = True
            triggers.append({
                "indicator": "Technical Domain Skills",
                "current_value": tech_skill,
                "threshold": f"< {self.place_th['technical_moderate']}",
                "severity": "Moderate",
                "message": f"Technical domain proficiency ({tech_skill:.1f}) is moderate."
            })

        # 5. Mock Interview & Soft Skills - distinguish missing from low
        if pd.isna(mock):
            pending_items.append("Mock Interview assessment is pending scheduling (not treated as negative score)")
        else:
            mock_val = float(mock)
            if mock_val < self.place_th["mock_critical"]:
                is_critical = True
                triggers.append({
                    "indicator": "Mock Interview",
                    "current_value": mock_val,
                    "threshold": f"< {self.place_th['mock_critical']}",
                    "severity": "Critical",
                    "message": f"Mock interview evaluation ({mock_val:.1f}) indicates severe interview readiness gaps."
                })
            elif mock_val < self.place_th["mock_moderate"]:
                is_moderate = True
                triggers.append({
                    "indicator": "Mock Interview",
                    "current_value": mock_val,
                    "threshold": f"< {self.place_th['mock_moderate']}",
                    "severity": "Moderate",
                    "message": f"Mock interview score ({mock_val:.1f}) indicates need for interview practice."
                })

        if pd.isna(soft):
            pending_items.append("Soft skills evaluation is scheduled for a future round")

        # Determine level
        if is_critical:
            level = "High"
            explanation = "High Placement Risk: Critical deficiencies in coding, aptitude, or overall placement readiness."
        elif is_moderate:
            level = "Moderate"
            explanation = "Moderate Placement Risk: Candidate meets baseline qualification but requires targeted practice before campus recruitment drives."
        else:
            level = "Low"
            explanation = "Low Placement Risk: Strong placement profile with competitive coding, aptitude, and readiness scores."

        return {
            "level": level,
            "explanation": explanation,
            "triggers_count": len(triggers),
            "triggers": triggers,
            "pending_assessments": pending_items
        }

    def _generate_overall_summary(self, acad_level: str, place_level: str) -> str:
        """Summarizes combined risk posture."""
        if acad_level == "High" and place_level == "High":
            return "Dual Critical Risk: Immediate intervention required in both academic standing and recruitment readiness."
        elif acad_level == "High":
            return "Academic Priority: Academic remediation (clearing backlogs and boosting attendance) must take precedence."
        elif place_level == "High":
            return "Career Priority: Strong/moderate academics but requires urgent placement preparation (coding & aptitude drills)."
        elif acad_level == "Moderate" or place_level == "Moderate":
            return "Monitoring Required: Moderate risk identified in one or more areas; proactive coaching advised."
        else:
            return "On Track: Student maintains exemplary academic standing and career preparation standards."

    def add_risk_columns_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Batch-evaluates risks across entire DataFrame and appends risk columns."""
        df_out = df.copy()
        acad_levels = []
        acad_counts = []
        place_levels = []
        place_counts = []
        overall_summaries = []

        for _, row in df_out.iterrows():
            res = self.assess_student_risks(row)
            acad_levels.append(res["academic_risk"]["level"])
            acad_counts.append(res["academic_risk"]["triggers_count"])
            place_levels.append(res["placement_risk"]["level"])
            place_counts.append(res["placement_risk"]["triggers_count"])
            overall_summaries.append(res["overall_risk_summary"])

        df_out["academic_risk_level"] = acad_levels
        df_out["academic_risk_triggers_count"] = acad_counts
        df_out["placement_risk_level"] = place_levels
        df_out["placement_risk_triggers_count"] = place_counts
        df_out["overall_risk_summary"] = overall_summaries

        return df_out
