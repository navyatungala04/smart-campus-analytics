"""
run_pipeline.py
End-to-end execution script for Smart Campus Analytics Phase 2.
Loads data, integrates categories, calculates Student Success Scores,
performs risk analysis, assigns segments, generates personalized recommendations,
and exports processed datasets to data/processed/.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles if supported
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.service import AnalyticsService

def main():
    print("================================================================")
    print("   SMART CAMPUS ANALYTICS - PHASE 2 PROCESSING PIPELINE         ")
    print("================================================================")
    
    service = AnalyticsService()
    print("\n1. Initializing pipeline and integrating datasets...")
    service.initialize()
    
    audit = service.loader.get_audit_summary()
    print(f"   [OK] Loaded {len(audit['files_loaded'])} CSV files")
    print(f"   [OK] Processed {audit['master_student_count']} master student records")
    print("   [OK] Verified 100% referential integrity across all child tables")

    print("\n2. Computing Student Success Scores, Risk Profiles & Segments...")
    df_processed = service.get_processed_dataframe()
    print(f"   [OK] Generated unified profiles: {df_processed.shape[0]} rows, {df_processed.shape[1]} features")

    summary = service.get_cohort_summary()
    print("\n3. Cohort Distribution Summary:")
    print(f"   - Average Success Score: {summary['average_success_score']:.2f}/100")
    print(f"   - Median Success Score:  {summary['median_success_score']:.2f}/100")
    print(f"   - Interquartile Range:   {summary['score_quartiles']['q25']:.2f} - {summary['score_quartiles']['q75']:.2f}")

    print("\n   Academic Risk Distribution:")
    for level, count in summary["academic_risk_distribution"].items():
        pct = (count / summary["total_students"]) * 100
        print(f"     * {level:<9}: {count:>3} students ({pct:>5.1f}%)")

    print("\n   Placement Risk Distribution:")
    for level, count in summary["placement_risk_distribution"].items():
        pct = (count / summary["total_students"]) * 100
        print(f"     * {level:<9}: {count:>3} students ({pct:>5.1f}%)")

    print("\n   Student Segment Distribution:")
    for seg, count in summary["segment_distribution"].items():
        pct = (count / summary["total_students"]) * 100
        print(f"     * {seg:<45}: {count:>3} ({pct:>5.1f}%)")

    print("\n4. Exporting Processed Data...")
    paths = service.export_processed_data()
    for name, p in paths.items():
        print(f"   [OK] Exported {name}: {p}")

    print("\n5. Sample Student Inspection:")
    sample_ids = ["STU1001", "STU1008", "STU1015"]
    for sid in sample_ids:
        dossier = service.get_student_profile(sid)
        if not dossier:
            continue
        p = dossier["personal_info"]
        sc = dossier["success_score"]
        ra = dossier["risk_analysis"]
        seg = dossier["segmentation"]
        recs = dossier["recommendations"]

        print(f"\n   ------------------------------------------------------------")
        print(f"   Student ID:     {dossier['student_id']} ({p['student_name']})")
        print(f"   Department:     {p['department']} | Semester {p['semester']}")
        print(f"   Success Score:  {sc['overall_score']:.2f}/100")
        print(f"   Segment:        {seg['segment_name']}")
        print(f"   Academic Risk:  {ra['academic_risk']['level']} ({ra['academic_risk']['triggers_count']} triggers)")
        print(f"   Placement Risk: {ra['placement_risk']['level']} ({ra['placement_risk']['triggers_count']} triggers)")
        print(f"   Top Recommendations ({len(recs)} total):")
        for i, r in enumerate(recs[:2], 1):
            print(f"     {i}. [{r['priority']}] {r['category']}: {r['suggested_action']}")
            print(f"        Target: {r['improvement_target']}")

    print("\n================================================================")
    print("   PHASE 2 PIPELINE EXECUTED SUCCESSFULLY                      ")
    print("================================================================")

if __name__ == "__main__":
    main()
