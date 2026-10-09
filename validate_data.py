"""
validate_data.py
Comprehensive validation script for Smart Campus Analytics Dataset (Phase 1).
Validates file existence, required schema, duplicate records, missing values,
value ranges, calculated field integrity, and cross-table foreign key consistency.
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure UTF-8 output on Windows consoles if supported
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REQUIRED_FILES = {
    "students.csv": [
        "student_id", "student_name", "department", "academic_year", "semester", "email"
    ],
    "academic.csv": [
        "student_id", "semester", "cgpa", "subject_name", "subject_marks", "backlogs"
    ],
    "attendance.csv": [
        "student_id", "subject_name", "classes_attended", "total_classes", "attendance_percentage"
    ],
    "lms_activity.csv": [
        "student_id", "login_frequency", "assignments_completed", "total_assignments", "assignment_completion_percentage"
    ],
    "engagement.csv": [
        "student_id", "events_attended", "clubs_participated", "hackathons_participated", "extracurricular_participation", "certifications_count"
    ],
    "placement.csv": [
        "student_id", "aptitude_score", "coding_score", "mock_interview_score", "placement_readiness_score"
    ],
    "skills.csv": [
        "student_id", "technical_skill_score", "soft_skill_score", "assessed_skills", "assessment_date"
    ],
    "feedback.csv": [
        "student_id", "student_satisfaction_score", "faculty_feedback_score", "feedback_date"
    ]
}

DATA_DIR = "data"

class DatasetValidator:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.dfs = {}
        self.errors = []
        self.warnings = []
        self.passed_checks = 0

    def log_error(self, message):
        self.errors.append(f"[ERROR] {message}")
        print(f"  [ERROR] {message}")

    def log_warning(self, message):
        self.warnings.append(f"[WARNING] {message}")
        print(f"  [WARN]  {message}")

    def log_pass(self, message):
        self.passed_checks += 1
        print(f"  [PASS]  {message}")

    def check_file_existence(self):
        print("\n--- 1. Checking File Existence ---")
        all_exist = True
        for filename in REQUIRED_FILES.keys():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                self.log_error(f"Missing required file: {filepath}")
                all_exist = False
                continue

            try:
                df = pd.read_csv(filepath)
                self.dfs[filename] = df
            except Exception as e:
                self.log_error(f"Failed to read {filepath}: {e}")
                all_exist = False
                continue

            self.log_pass(f"{filename} exists ({len(df)} rows, {len(df.columns)} columns)")

        return all_exist

    def check_schema_and_columns(self):
        print("\n--- 2. Checking Column Schemas ---")
        for filename, expected_cols in REQUIRED_FILES.items():
            if filename not in self.dfs:
                continue
            df = self.dfs[filename]
            actual_cols = list(df.columns)
            missing = [c for c in expected_cols if c not in actual_cols]
            extra = [c for c in actual_cols if c not in expected_cols]

            if missing:
                self.log_error(f"{filename} is missing columns: {missing}")
            elif extra:
                self.log_warning(f"{filename} has unexpected extra columns: {extra}")
            else:
                self.log_pass(f"{filename} matches expected schema ({len(actual_cols)} columns)")

    def check_duplicates(self):
        print("\n--- 3. Checking Duplicate Records ---")
        pk_definitions = {
            "students.csv": ["student_id"],
            "academic.csv": ["student_id", "subject_name"],
            "attendance.csv": ["student_id", "subject_name"],
            "lms_activity.csv": ["student_id"],
            "engagement.csv": ["student_id"],
            "placement.csv": ["student_id"],
            "skills.csv": ["student_id"],
            "feedback.csv": ["student_id"],
        }
        for filename, pks in pk_definitions.items():
            if filename not in self.dfs:
                continue
            df = self.dfs[filename]
            exact_dups = df.duplicated().sum()
            if exact_dups > 0:
                self.log_error(f"{filename} has {exact_dups} duplicate rows")
            
            key_dups = df.duplicated(subset=pks).sum()
            if key_dups > 0:
                self.log_error(f"{filename} has {key_dups} duplicate keys on {pks}")
            else:
                self.log_pass(f"{filename} has zero duplicate keys on {pks}")

    def check_missing_values(self):
        print("\n--- 4. Checking Missing Values & Null Distributions ---")
        allowed_null_columns = {
            "placement.csv": ["mock_interview_score"],
            "skills.csv": ["soft_skill_score"],
            "feedback.csv": ["student_satisfaction_score"]
        }

        for filename, df in self.dfs.items():
            null_counts = df.isnull().sum()
            cols_with_nulls = null_counts[null_counts > 0]
            if len(cols_with_nulls) == 0:
                self.log_pass(f"{filename} has 0 missing values (100% complete)")
            else:
                for col, count in cols_with_nulls.items():
                    pct = (count / len(df)) * 100
                    allowed = allowed_null_columns.get(filename, [])
                    if col in allowed:
                        if pct <= 15.0:
                            self.log_pass(f"{filename}: '{col}' has {count} acceptable missing values ({pct:.1f}%) [Realistic synthetic scenario]")
                        else:
                            self.log_warning(f"{filename}: '{col}' has high missing rate: {pct:.1f}% ({count} rows)")
                    else:
                        self.log_error(f"{filename}: unexpected null values in mandatory column '{col}': {count} missing")

    def check_referential_integrity(self):
        print("\n--- 5. Checking Referential Integrity (Student IDs) ---")
        if "students.csv" not in self.dfs:
            self.log_error("Cannot verify referential integrity: students.csv missing")
            return

        master_ids = set(self.dfs["students.csv"]["student_id"])
        self.log_pass(f"Master student count: {len(master_ids)} unique students")

        if len(master_ids) < 100:
            self.log_error(f"Requirement requires at least 100 students, found {len(master_ids)}")
        else:
            self.log_pass(f"Student count requirement satisfied: {len(master_ids)} students (>= 100)")

        for filename, df in self.dfs.items():
            if filename == "students.csv" or "student_id" not in df.columns:
                continue
            child_ids = set(df["student_id"])
            orphan_ids = child_ids - master_ids
            if orphan_ids:
                self.log_error(f"{filename} contains {len(orphan_ids)} orphan student IDs not in students.csv: {orphan_ids}")
            else:
                missing_students = master_ids - child_ids
                if missing_students:
                    self.log_warning(f"{filename} is missing records for {len(missing_students)} students from students.csv")
                else:
                    self.log_pass(f"{filename} student IDs 100% consistent with students.csv")

    def check_calculated_fields_and_logic(self):
        print("\n--- 6. Checking Calculated Fields & Mathematical Logic ---")
        # Attendance calculation
        if "attendance.csv" in self.dfs:
            df = self.dfs["attendance.csv"]
            calc_att = np.round((df["classes_attended"] / df["total_classes"]) * 100.0, 2)
            mismatch = (np.abs(calc_att - df["attendance_percentage"]) > 0.05).sum()
            overflow = (df["classes_attended"] > df["total_classes"]).sum()
            negative = (df["classes_attended"] < 0).sum()
            if mismatch > 0:
                self.log_error(f"attendance.csv: {mismatch} rows have incorrect attendance_percentage calculation")
            elif overflow > 0:
                self.log_error(f"attendance.csv: {overflow} rows have classes_attended > total_classes")
            elif negative > 0:
                self.log_error(f"attendance.csv: {negative} rows have classes_attended < 0")
            else:
                self.log_pass("attendance.csv: attendance_percentage matches classes_attended / total_classes exactly")

        # LMS Activity calculation
        if "lms_activity.csv" in self.dfs:
            df = self.dfs["lms_activity.csv"]
            calc_assign = np.round((df["assignments_completed"] / df["total_assignments"]) * 100.0, 2)
            mismatch = (np.abs(calc_assign - df["assignment_completion_percentage"]) > 0.05).sum()
            overflow = (df["assignments_completed"] > df["total_assignments"]).sum()
            negative = (df["assignments_completed"] < 0).sum()
            if mismatch > 0:
                self.log_error(f"lms_activity.csv: {mismatch} rows have incorrect assignment_completion_percentage calculation")
            elif overflow > 0:
                self.log_error(f"lms_activity.csv: {overflow} rows have assignments_completed > total_assignments")
            elif negative > 0:
                self.log_error(f"lms_activity.csv: {negative} rows have negative assignments")
            else:
                self.log_pass("lms_activity.csv: assignment_completion_percentage matches assignments_completed / total_assignments exactly")

    def check_value_ranges(self):
        print("\n--- 7. Checking Value Ranges & Categorical Validity ---")
        # Students
        if "students.csv" in self.dfs:
            df = self.dfs["students.csv"]
            if not df["semester"].between(1, 8).all():
                self.log_error("students.csv: semester outside valid range [1, 8]")
            else:
                self.log_pass("students.csv: semester values valid [1-8]")

            invalid_emails = (~df["email"].str.contains(r"^.+@smartcampus\.edu$", regex=True)).sum()
            if invalid_emails > 0:
                self.log_error(f"students.csv: {invalid_emails} invalid email formats")
            else:
                self.log_pass("students.csv: all emails follow standard domain format")

        # Academic
        if "academic.csv" in self.dfs:
            df = self.dfs["academic.csv"]
            if not df["cgpa"].between(0.0, 10.0).all():
                self.log_error("academic.csv: cgpa outside [0.0, 10.0]")
            elif not df["subject_marks"].between(0.0, 100.0).all():
                self.log_error("academic.csv: subject_marks outside [0.0, 100.0]")
            elif not (df["backlogs"] >= 0).all():
                self.log_error("academic.csv: negative backlogs found")
            else:
                self.log_pass("academic.csv: cgpa, subject_marks, and backlogs all within valid bounds")

        # Attendance
        if "attendance.csv" in self.dfs:
            df = self.dfs["attendance.csv"]
            if not df["attendance_percentage"].between(0.0, 100.0).all():
                self.log_error("attendance.csv: attendance_percentage outside [0.0, 100.0]")
            else:
                self.log_pass("attendance.csv: attendance_percentage within valid range [0, 100]")

        # LMS Activity
        if "lms_activity.csv" in self.dfs:
            df = self.dfs["lms_activity.csv"]
            if not (df["login_frequency"] >= 0).all():
                self.log_error("lms_activity.csv: login_frequency cannot be negative")
            elif not df["assignment_completion_percentage"].between(0.0, 100.0).all():
                self.log_error("lms_activity.csv: assignment_completion_percentage outside [0, 100]")
            else:
                self.log_pass("lms_activity.csv: login_frequency and assignment_completion_percentage valid")

        # Engagement
        if "engagement.csv" in self.dfs:
            df = self.dfs["engagement.csv"]
            valid_ec = {"High", "Medium", "Low"}
            invalid_ec = (~df["extracurricular_participation"].isin(valid_ec)).sum()
            if invalid_ec > 0:
                self.log_error(f"engagement.csv: {invalid_ec} invalid extracurricular_participation categories")
            elif not (df["events_attended"] >= 0).all() or not (df["clubs_participated"] >= 0).all() or not (df["hackathons_participated"] >= 0).all() or not (df["certifications_count"] >= 0).all():
                self.log_error("engagement.csv: negative values found in counts")
            else:
                self.log_pass("engagement.csv: all count columns >= 0 and participation levels valid")

        # Placement
        if "placement.csv" in self.dfs:
            df = self.dfs["placement.csv"]
            non_null_mock = df["mock_interview_score"].dropna()
            if not df["aptitude_score"].between(0.0, 100.0).all():
                self.log_error("placement.csv: aptitude_score outside [0, 100]")
            elif not df["coding_score"].between(0.0, 100.0).all():
                self.log_error("placement.csv: coding_score outside [0, 100]")
            elif not non_null_mock.between(0.0, 100.0).all():
                self.log_error("placement.csv: mock_interview_score outside [0, 100]")
            elif not df["placement_readiness_score"].between(0.0, 100.0).all():
                self.log_error("placement.csv: placement_readiness_score outside [0, 100]")
            else:
                self.log_pass("placement.csv: aptitude, coding, mock interview, and readiness scores within [0, 100]")

        # Skills
        if "skills.csv" in self.dfs:
            df = self.dfs["skills.csv"]
            non_null_soft = df["soft_skill_score"].dropna()
            if not df["technical_skill_score"].between(0.0, 100.0).all():
                self.log_error("skills.csv: technical_skill_score outside [0, 100]")
            elif not non_null_soft.between(0.0, 100.0).all():
                self.log_error("skills.csv: soft_skill_score outside [0, 100]")
            else:
                self.log_pass("skills.csv: technical and soft skill scores within [0, 100]")

        # Feedback
        if "feedback.csv" in self.dfs:
            df = self.dfs["feedback.csv"]
            non_null_sat = df["student_satisfaction_score"].dropna()
            if not non_null_sat.between(1.0, 5.0).all():
                self.log_error("feedback.csv: student_satisfaction_score outside [1.0, 5.0]")
            elif not df["faculty_feedback_score"].between(1.0, 5.0).all():
                self.log_error("feedback.csv: faculty_feedback_score outside [1.0, 5.0]")
            else:
                self.log_pass("feedback.csv: satisfaction and faculty scores within rating scale [1.0, 5.0]")

    def run_all(self):
        print("================================================================")
        print("   SMART CAMPUS ANALYTICS - DATASET VALIDATION (PHASE 1)        ")
        print("================================================================")
        
        if not self.check_file_existence():
            print("\nCritical files missing. Validation halted.")
            return False

        self.check_schema_and_columns()
        self.check_duplicates()
        self.check_missing_values()
        self.check_referential_integrity()
        self.check_calculated_fields_and_logic()
        self.check_value_ranges()

        print("\n================================================================")
        print("                     VALIDATION SUMMARY                         ")
        print("================================================================")
        print(f"Passed Checks: {self.passed_checks}")
        print(f"Warnings:      {len(self.warnings)}")
        print(f"Errors:        {len(self.errors)}")

        if self.warnings:
            print("\nWarnings:")
            for w in self.warnings:
                print(f"  {w}")

        if self.errors:
            print("\nErrors Found:")
            for e in self.errors:
                print(f"  {e}")
            print("\nStatus: FAILED")
            return False
        else:
            print("\nStatus: ALL CHECKS PASSED SUCCESSFULLY")
            return True

if __name__ == "__main__":
    validator = DatasetValidator()
    success = validator.run_all()
    sys.exit(0 if success else 1)
