"""
data_loader.py
Robust data loading module for Smart Campus Analytics Phase 2.
Reads, validates file integrity, audits duplicates, handles missing values,
and verifies referential relationships across all seven data categories.
"""

import os
from typing import Dict, Any, Tuple
import pandas as pd
from src.config import DEFAULT_DATA_DIR

REQUIRED_FILES = [
    "students.csv",
    "academic.csv",
    "attendance.csv",
    "lms_activity.csv",
    "engagement.csv",
    "placement.csv",
    "skills.csv",
    "feedback.csv"
]

class DataLoader:
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.raw_data: Dict[str, pd.DataFrame] = {}
        self.load_audit: Dict[str, Any] = {
            "files_loaded": [],
            "row_counts": {},
            "null_counts": {},
            "duplicate_counts": {},
            "master_student_count": 0,
            "referential_integrity_valid": True
        }

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Loads and validates all 8 CSV files into DataFrames."""
        for filename in REQUIRED_FILES:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Required dataset not found: {filepath}")

            df = pd.read_csv(filepath)
            name_key = filename.replace(".csv", "")
            self.raw_data[name_key] = df
            self.load_audit["files_loaded"].append(filename)
            self.load_audit["row_counts"][name_key] = len(df)
            
            # Check for exact duplicate rows
            dup_count = int(df.duplicated().sum())
            self.load_audit["duplicate_counts"][name_key] = dup_count
            if dup_count > 0:
                # Deduplicate exact duplicate rows to prevent distorted aggregations
                self.raw_data[name_key] = df.drop_duplicates()

            # Record missing value audit
            nulls = df.isnull().sum().to_dict()
            active_nulls = {k: int(v) for k, v in nulls.items() if v > 0}
            if active_nulls:
                self.load_audit["null_counts"][name_key] = active_nulls

        self._validate_relationships()
        return self.raw_data

    def _validate_relationships(self) -> None:
        """Ensures all child tables reference valid student_ids present in students.csv."""
        if "students" not in self.raw_data:
            raise ValueError("students master DataFrame not found")

        df_students = self.raw_data["students"]
        master_ids = set(df_students["student_id"])
        self.load_audit["master_student_count"] = len(master_ids)

        if len(master_ids) == 0:
            raise ValueError("Master students dataset is empty")

        for name_key, df in self.raw_data.items():
            if name_key == "students" or "student_id" not in df.columns:
                continue

            child_ids = set(df["student_id"])
            orphan_ids = child_ids - master_ids
            if orphan_ids:
                self.load_audit["referential_integrity_valid"] = False
                raise ValueError(
                    f"Referential integrity violation in '{name_key}': "
                    f"Found {len(orphan_ids)} orphan student IDs not in students.csv: {list(orphan_ids)[:5]}"
                )

    def get_audit_summary(self) -> Dict[str, Any]:
        """Returns diagnostic metadata about the loaded datasets."""
        return self.load_audit
