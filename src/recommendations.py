"""
recommendations.py
Personalized student recommendation engine for Smart Campus Analytics Phase 2.
Generates tailored, actionable improvement plans with measurable targets,
priorities, and concrete reasons derived from individual student indicators.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

class RecommendationEngine:
    def generate_recommendations(self, student_row: pd.Series) -> List[Dict[str, Any]]:
        """Generates prioritized, personalized recommendations for a student."""
        recs: List[Dict[str, Any]] = []

        # 1. Backlogs Recommendation
        backlogs = int(student_row.get("backlogs", 0))
        if backlogs > 0:
            recs.append({
                "id": "rec_academic_backlogs",
                "category": "Academic Clearance",
                "priority": "Critical" if backlogs >= 2 else "High",
                "related_metric": "backlogs",
                "current_value": f"{backlogs} active backlog(s)",
                "improvement_target": "0 active backlogs (clear in upcoming remedial exams)",
                "reason": f"Active backlogs ({backlogs}) restrict company placement eligibility and degree progression.",
                "suggested_action": (
                    f"Enroll in university remedial coaching for uncleared subjects, meet faculty advisors weekly, "
                    f"and allocate 6 dedicated hours per week to backlog coursework."
                )
            })

        # 2. Attendance Improvement Plan
        att_pct = float(student_row.get("overall_attendance_percentage", 100.0))
        total_att = int(student_row.get("total_classes_attended", 0))
        total_sch = int(student_row.get("total_classes_scheduled", 0))
        low_att_subs = int(student_row.get("low_attendance_subjects_count", 0))

        if att_pct < 75.0:
            # Calculate classes needed to reach 75%:
            # (total_att + x) / (total_sch + x) >= 0.75  =>  0.25*x >= 0.75*total_sch - total_att
            needed = max(1, int(np.ceil((0.75 * total_sch - total_att) / 0.25)))
            priority = "Critical" if att_pct < 65.0 else "High"
            recs.append({
                "id": "rec_attendance_recovery",
                "category": "Attendance Recovery",
                "priority": priority,
                "related_metric": "overall_attendance_percentage",
                "current_value": f"{att_pct:.2f}% ({total_att}/{total_sch} classes)",
                "improvement_target": f">= 75.00% (attend next {needed} consecutive classes without absence)",
                "reason": (
                    f"Current attendance is below the mandatory 75% institutional requirement. "
                    f"{low_att_subs} subject(s) are at risk of exam debarment."
                ),
                "suggested_action": (
                    f"Maintain 100% attendance over the next {needed} scheduled lectures. "
                    f"Submit medical or leave certificates for excused prior absences to academic dean."
                )
            })
        elif att_pct < 80.0:
            recs.append({
                "id": "rec_attendance_buffer",
                "category": "Attendance Buffer",
                "priority": "Medium",
                "related_metric": "overall_attendance_percentage",
                "current_value": f"{att_pct:.2f}%",
                "improvement_target": ">= 85.00%",
                "reason": "Attendance is marginally above the 75% cutoff, leaving little margin for unforeseen illness or emergencies.",
                "suggested_action": "Avoid non-essential leaves and build an attendance buffer above 85%."
            })

        # 3. LMS Assignment Completion
        assign_pct = float(student_row.get("assignment_completion_percentage", 100.0))
        assign_comp = int(student_row.get("assignments_completed", 0))
        assign_total = int(student_row.get("total_assignments", 12))
        missing_assign = assign_total - assign_comp

        if assign_pct < 75.0:
            priority = "Critical" if assign_pct < 50.0 else "High"
            recs.append({
                "id": "rec_lms_assignments",
                "category": "LMS Coursework",
                "priority": priority,
                "related_metric": "assignment_completion_percentage",
                "current_value": f"{assign_pct:.2f}% ({assign_comp}/{assign_total} completed)",
                "improvement_target": f">= 85.00% (submit remaining {missing_assign} assignments)",
                "reason": f"{missing_assign} unsubmitted assignments are negatively impacting your internal assessment scores.",
                "suggested_action": (
                    f"Access the LMS portal, complete overdue assignments during faculty review hours, "
                    f"and set weekly calendar reminders for submission deadlines."
                )
            })

        # 4. Coding Proficiency & Technical Assessments
        cod_score = float(student_row.get("coding_score", 100.0))
        tech_score = float(student_row.get("technical_skill_score", 100.0))

        if cod_score < 70.0:
            priority = "Critical" if cod_score < 50.0 else "High"
            recs.append({
                "id": "rec_coding_skills",
                "category": "Coding & Algorithms",
                "priority": priority,
                "related_metric": "coding_score",
                "current_value": f"{cod_score:.1f}/100",
                "improvement_target": ">= 75.0/100 (solve 30 medium DSA problems)",
                "reason": "Technical recruitment screens require strong data structures and algorithmic implementation speed.",
                "suggested_action": (
                    "Practice 1-2 coding problems daily on LeetCode/HackerRank focusing on Arrays, Strings, "
                    "Hashing, and Binary Search. Participate in weekly campus coding contests."
                )
            })

        # 5. Quantitative & Logical Aptitude
        apt_score = float(student_row.get("aptitude_score", 100.0))
        if apt_score < 70.0:
            priority = "High" if apt_score < 55.0 else "Medium"
            recs.append({
                "id": "rec_aptitude_reasoning",
                "category": "Aptitude & Reasoning",
                "priority": priority,
                "related_metric": "aptitude_score",
                "current_value": f"{apt_score:.1f}/100",
                "improvement_target": ">= 75.0/100",
                "reason": "Campus placement round 1 relies on strict quantitative and logical aptitude cutoffs.",
                "suggested_action": (
                    "Complete daily 20-minute timed speed math and logical reasoning quizzes on the campus placement portal. "
                    "Review high-frequency topics: Percentages, Profit & Loss, Ratios, and Syllogisms."
                )
            })

        # 6. Mock Interview & Soft Skills
        mock_score = student_row.get("mock_interview_score")
        soft_score = student_row.get("soft_skill_score")

        if pd.isna(mock_score):
            recs.append({
                "id": "rec_mock_interview_pending",
                "category": "Placement Assessment Scheduling",
                "priority": "High",
                "related_metric": "mock_interview_score",
                "current_value": "Pending Evaluation",
                "improvement_target": "Complete 1 Diagnostic Mock Interview",
                "reason": "You have not yet attended your scheduled diagnostic mock interview with placement mentors.",
                "suggested_action": (
                    "Book an interview slot with the career cell this week to receive baseline feedback on "
                    "resume presentation, communication, and system design."
                )
            })
        elif float(mock_score) < 70.0:
            priority = "High" if float(mock_score) < 55.0 else "Medium"
            recs.append({
                "id": "rec_mock_interview_prep",
                "category": "Interview Preparation",
                "priority": priority,
                "related_metric": "mock_interview_score",
                "current_value": f"{float(mock_score):.1f}/100",
                "improvement_target": ">= 75.0/100 in Next Mock Round",
                "reason": "Mock interview feedback indicates need for sharper communication and project articulation.",
                "suggested_action": (
                    "Practice explaining your major projects using the STAR method (Situation, Task, Action, Result). "
                    "Conduct peer mock interviews twice a week."
                )
            })

        if pd.notna(soft_score) and float(soft_score) < 65.0:
            recs.append({
                "id": "rec_soft_skills",
                "category": "Soft Skills & Communication",
                "priority": "Medium",
                "related_metric": "soft_skill_score",
                "current_value": f"{float(soft_score):.1f}/100",
                "improvement_target": ">= 75.0/100",
                "reason": "Interpersonal and presentation skill scores require enhancement for corporate HR rounds.",
                "suggested_action": (
                    "Join the campus Toastmasters / Debate Club and participate in group discussions during weekly communication labs."
                )
            })

        # 7. Co-curricular Engagement & Hackathons
        hackathons = int(student_row.get("hackathons_participated", 0))
        clubs = int(student_row.get("clubs_participated", 0))
        certs = int(student_row.get("certifications_count", 0))

        if hackathons == 0 and clubs == 0:
            recs.append({
                "id": "rec_campus_engagement",
                "category": "Campus Engagement",
                "priority": "Medium",
                "related_metric": "engagement_score",
                "current_value": "0 clubs, 0 hackathons",
                "improvement_target": "Join 1 technical club & register for 1 hackathon",
                "reason": "Lack of extracurricular and collaborative activities weakens resume differentiation for tier-1 companies.",
                "suggested_action": (
                    "Register for the upcoming internal Smart Campus Hackathon and sign up for a department technical club."
                )
            })
        elif certs == 0:
            recs.append({
                "id": "rec_industry_certification",
                "category": "Industry Certification",
                "priority": "Low",
                "related_metric": "certifications_count",
                "current_value": "0 certifications",
                "improvement_target": "Earn 1 verified industry certificate",
                "reason": "Industry credentials in cloud, AI, or full-stack technologies validate specialized domain proficiency.",
                "suggested_action": "Enroll in a subsidized AWS, Google Cloud, or Coursera specialization via the campus learning portal."
            })

        # 8. High Performer Growth Recommendations (If no critical or high weaknesses)
        high_priority_count = sum(1 for r in recs if r["priority"] in ["Critical", "High"])
        if high_priority_count == 0:
            recs.append({
                "id": "rec_excellence_leadership",
                "category": "Excellence & Leadership",
                "priority": "Low",
                "related_metric": "student_success_score",
                "current_value": f"{float(student_row.get('student_success_score', 85.0)):.1f}/100",
                "improvement_target": "Mentorship & Tier-1 Competitive Placement",
                "reason": "Exemplary academic and placement standing across all core performance dimensions.",
                "suggested_action": (
                    "Serve as a peer mentor in junior study circles, lead a team in national hackathons (e.g. Smart India Hackathon), "
                    "and prepare for dream company off-campus hiring drives."
                )
            })

        # Sort recommendations by priority order: Critical -> High -> Medium -> Low
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        recs.sort(key=lambda x: priority_order.get(x["priority"], 4))

        return recs
