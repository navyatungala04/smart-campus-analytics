"""
generate_synthetic_data.py
Generates realistic synthetic data for Smart Campus Analytics Phase 1.
Covers 120 fictional students across 8 CSV files.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_all_datasets():
    np.random.seed(42)
    random.seed(42)

    os.makedirs("data", exist_ok=True)
    num_students = 120

    # 1. Generate Students Master Dataset
    first_names = [
        "Aarav", "Aditi", "Akhil", "Ananya", "Arjun", "Bhavya", "Chetan", "Deepa",
        "Dev", "Divya", "Gautam", "Harini", "Ishaan", "Janani", "Karthik", "Kavya",
        "Kiran", "Lakshmi", "Madhav", "Meera", "Naveen", "Neha", "Nikhil", "Pooja",
        "Pranav", "Priya", "Rahul", "Rhea", "Rishi", "Rohan", "Sahil", "Sanjay",
        "Shreya", "Siddharth", "Sneha", "Surya", "Tanvi", "Tarun", "Varun", "Vidya",
        "Vikram", "Yash", "Aditya", "Amrita", "Anirudh", "Archana", "Ashwin", "Chaithra",
        "Dinesh", "Gayathri", "Hari", "Indira", "Jagan", "Keerthi", "Manish", "Nandita",
        "Pavithra", "Raghav", "Sangeetha", "Tejas", "Uma", "Vandana", "Vignesh", "Zoya"
    ]
    last_names = [
        "Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Rao", "Kumar",
        "Singh", "Menon", "Pillai", "Gupta", "Deshmukh", "Joshi", "Bose", "Ghosh",
        "Kulkarni", "Bhat", "Chopra", "Mehta", "Saxena", "Sengupta", "Das", "Rajan",
        "Swaminathan", "Narayanan", "Shetty", "Gowda", "Balakrishnan", "Chatterjee"
    ]

    departments = ["Computer Science and Engineering", "Information Technology", 
                   "Electronics and Communication Engineering", "Data Science", "Mechanical Engineering"]
    dept_codes = {
        "Computer Science and Engineering": "cse",
        "Information Technology": "it",
        "Electronics and Communication Engineering": "ece",
        "Data Science": "ds",
        "Mechanical Engineering": "mech"
    }

    students = []
    student_ids = [f"STU{1001 + i}" for i in range(num_students)]

    # Distribute student profiles to reflect realistic academic performance clusters:
    # 0: High Achievers (~20%)
    # 1: Steady / Average (~45%)
    # 2: Struggling / Needs Support (~20%)
    # 3: At-Risk (~10%)
    # 4: Practical Hacker / Specialist (~5%)
    profiles = np.random.choice([0, 1, 2, 3, 4], size=num_students, p=[0.20, 0.45, 0.20, 0.10, 0.05])

    for i in range(num_students):
        s_id = student_ids[i]
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        full_name = f"{fname} {lname}"
        
        # Academic year and semester (Years 2, 3, 4 for comprehensive placement & LMS analytics)
        # 2nd year: sem 3; 3rd year: sem 5; 4th year: sem 7
        year_idx = np.random.choice([2, 3, 4], p=[0.30, 0.45, 0.25])
        sem_map = {2: 3, 3: 5, 4: 7}
        semester = sem_map[year_idx]
        dept = departments[i % len(departments)]
        clean_name = f"{fname.lower()}.{lname.lower()}"
        email = f"{clean_name}{s_id[-3:]}@smartcampus.edu"
        
        students.append({
            "student_id": s_id,
            "student_name": full_name,
            "department": dept,
            "academic_year": f"{year_idx}nd Year" if year_idx == 2 else f"{year_idx}rd Year" if year_idx == 3 else f"{year_idx}th Year",
            "semester": semester,
            "email": email
        })

    df_students = pd.DataFrame(students)
    df_students.to_csv("data/students.csv", index=False)
    print(f"Generated data/students.csv ({len(df_students)} rows)")

    # 2. Subject dictionary per department and semester
    dept_subjects = {
        "Computer Science and Engineering": {
            3: ["Data Structures", "Digital Logic & Design", "Object Oriented Programming", "Discrete Mathematics"],
            5: ["Database Management Systems", "Operating Systems", "Design & Analysis of Algorithms", "Computer Networks"],
            7: ["Artificial Intelligence", "Cloud Computing", "Information Security", "Compiler Design"]
        },
        "Information Technology": {
            3: ["Data Structures", "Computer Organization", "Java Programming", "Discrete Mathematics"],
            5: ["Database Systems", "Web Technology", "Operating Systems", "Software Engineering"],
            7: ["Cloud Infrastructure", "Cyber Security", "Big Data Analytics", "Mobile Computing"]
        },
        "Electronics and Communication Engineering": {
            3: ["Electronic Devices & Circuits", "Digital Electronics", "Signals and Systems", "Network Theory"],
            5: ["Microprocessors & Microcontrollers", "Digital Signal Processing", "Analog Communication", "Electromagnetic Fields"],
            7: ["VLSI Design", "Wireless Communication", "Embedded Systems", "Optical Networks"]
        },
        "Data Science": {
            3: ["Python for Data Science", "Data Structures", "Linear Algebra & Statistics", "Database Systems"],
            5: ["Machine Learning", "Data Mining & Warehousing", "Operating Systems", "Applied Statistics"],
            7: ["Deep Learning", "Natural Language Processing", "Big Data Engineering", "Data Visualization & BI"]
        },
        "Mechanical Engineering": {
            3: ["Thermodynamics", "Fluid Mechanics", "Engineering Mechanics", "Materials Science"],
            5: ["Heat Transfer", "Kinematics of Machinery", "Design of Machine Elements", "Manufacturing Technology"],
            7: ["CAD/CAM & Automation", "Robotics & Automation", "Finite Element Analysis", "Power Plant Engineering"]
        }
    }

    # Generate Data for Each Student
    academic_records = []
    attendance_records = []
    lms_records = []
    engagement_records = []
    placement_records = []
    skills_records = []
    feedback_records = []

    for i, s_row in df_students.iterrows():
        s_id = s_row["student_id"]
        sem = s_row["semester"]
        dept = s_row["department"]
        profile = profiles[i]
        
        # Profile baseline characteristics:
        if profile == 0:  # High Achiever
            cgpa = round(np.random.uniform(8.60, 9.85), 2)
            backlogs = 0
            base_attendance_pct = np.random.uniform(88, 98)
            base_marks = np.random.uniform(82, 98)
            login_freq = np.random.randint(40, 65)
            total_assign = 12
            completed_assign = np.random.choice([11, 12], p=[0.2, 0.8])
            events = np.random.randint(5, 12)
            clubs = np.random.randint(2, 4)
            hackathons = np.random.randint(2, 6)
            ec_part = "High"
            certs = np.random.randint(3, 6)
            apt_score = round(np.random.uniform(85, 98), 1)
            cod_score = round(np.random.uniform(85, 98), 1)
            mock_score = round(np.random.uniform(82, 96), 1)
            tech_skill = round(np.random.uniform(85, 96), 1)
            soft_skill = round(np.random.uniform(82, 95), 1)
            sat_score = round(np.random.uniform(4.2, 5.0), 1)
            fac_score = round(np.random.uniform(4.3, 5.0), 1)

        elif profile == 1:  # Steady / Average
            cgpa = round(np.random.uniform(7.00, 8.50), 2)
            backlogs = 0
            base_attendance_pct = np.random.uniform(75, 87)
            base_marks = np.random.uniform(68, 83)
            login_freq = np.random.randint(22, 40)
            total_assign = 12
            completed_assign = np.random.randint(9, 12)
            events = np.random.randint(2, 6)
            clubs = np.random.randint(1, 3)
            hackathons = np.random.randint(0, 3)
            ec_part = np.random.choice(["Medium", "High"], p=[0.75, 0.25])
            certs = np.random.randint(1, 4)
            apt_score = round(np.random.uniform(68, 84), 1)
            cod_score = round(np.random.uniform(65, 82), 1)
            mock_score = round(np.random.uniform(65, 82), 1)
            tech_skill = round(np.random.uniform(68, 83), 1)
            soft_skill = round(np.random.uniform(68, 84), 1)
            sat_score = round(np.random.uniform(3.5, 4.4), 1)
            fac_score = round(np.random.uniform(3.6, 4.4), 1)

        elif profile == 2:  # Underperforming / Needs Support
            cgpa = round(np.random.uniform(5.50, 6.90), 2)
            backlogs = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
            base_attendance_pct = np.random.uniform(66, 76)
            base_marks = np.random.uniform(52, 68)
            login_freq = np.random.randint(12, 24)
            total_assign = 12
            completed_assign = np.random.randint(6, 10)
            events = np.random.randint(0, 4)
            clubs = np.random.randint(0, 2)
            hackathons = np.random.randint(0, 2)
            ec_part = np.random.choice(["Low", "Medium"], p=[0.7, 0.3])
            certs = np.random.choice([0, 1, 2], p=[0.5, 0.4, 0.1])
            apt_score = round(np.random.uniform(50, 67), 1)
            cod_score = round(np.random.uniform(48, 66), 1)
            mock_score = round(np.random.uniform(50, 66), 1)
            tech_skill = round(np.random.uniform(52, 67), 1)
            soft_skill = round(np.random.uniform(52, 67), 1)
            sat_score = round(np.random.uniform(2.8, 3.7), 1)
            fac_score = round(np.random.uniform(2.8, 3.6), 1)

        elif profile == 3:  # At-Risk / Critical attention
            cgpa = round(np.random.uniform(4.10, 5.40), 2)
            backlogs = np.random.choice([1, 2, 3, 4], p=[0.2, 0.4, 0.3, 0.1])
            base_attendance_pct = np.random.uniform(48, 64)
            base_marks = np.random.uniform(38, 54)
            login_freq = np.random.randint(5, 14)
            total_assign = 12
            completed_assign = np.random.randint(3, 7)
            events = np.random.randint(0, 2)
            clubs = np.random.choice([0, 1], p=[0.85, 0.15])
            hackathons = 0
            ec_part = "Low"
            certs = 0
            apt_score = round(np.random.uniform(32, 50), 1)
            cod_score = round(np.random.uniform(30, 48), 1)
            mock_score = round(np.random.uniform(32, 50), 1)
            tech_skill = round(np.random.uniform(35, 50), 1)
            soft_skill = round(np.random.uniform(35, 52), 1)
            sat_score = round(np.random.uniform(2.0, 3.0), 1)
            fac_score = round(np.random.uniform(2.0, 3.0), 1)

        else:  # Practical Hacker / Specialist
            cgpa = round(np.random.uniform(6.60, 7.60), 2)
            backlogs = np.random.choice([0, 1], p=[0.75, 0.25])
            base_attendance_pct = np.random.uniform(70, 80)
            base_marks = np.random.uniform(62, 78)
            login_freq = np.random.randint(28, 48)
            total_assign = 12
            completed_assign = np.random.randint(8, 11)
            events = np.random.randint(4, 9)
            clubs = np.random.randint(1, 3)
            hackathons = np.random.randint(4, 8)
            ec_part = "High"
            certs = np.random.randint(2, 5)
            apt_score = round(np.random.uniform(72, 86), 1)
            cod_score = round(np.random.uniform(92, 99), 1)  # Outstanding coding
            mock_score = round(np.random.uniform(75, 88), 1)
            tech_skill = round(np.random.uniform(88, 97), 1)
            soft_skill = round(np.random.uniform(66, 78), 1)
            sat_score = round(np.random.uniform(3.6, 4.6), 1)
            fac_score = round(np.random.uniform(3.5, 4.5), 1)

        # Subjects for student's department and semester
        subjects = dept_subjects[dept][sem]
        for sub in subjects:
            # Subject marks around base_marks with slight variance
            sub_mark = max(25.0, min(99.0, round(base_marks + np.random.normal(0, 4.5), 1)))
            academic_records.append({
                "student_id": s_id,
                "semester": sem,
                "cgpa": cgpa,
                "subject_name": sub,
                "subject_marks": sub_mark,
                "backlogs": backlogs
            })

            # Attendance per subject
            total_cls = random.choice([48, 50, 52, 54])
            # calculate attended classes from base percentage with minor variation
            sub_att_pct = max(35.0, min(98.0, base_attendance_pct + np.random.normal(0, 3.5)))
            att_cls = int(round((sub_att_pct / 100.0) * total_cls))
            att_cls = min(total_cls, max(12, att_cls))
            actual_pct = round((att_cls / total_cls) * 100.0, 2)
            
            attendance_records.append({
                "student_id": s_id,
                "subject_name": sub,
                "classes_attended": att_cls,
                "total_classes": total_cls,
                "attendance_percentage": actual_pct
            })

        # LMS Activity
        assign_pct = round((completed_assign / total_assign) * 100.0, 2)
        lms_records.append({
            "student_id": s_id,
            "login_frequency": login_freq,
            "assignments_completed": completed_assign,
            "total_assignments": total_assign,
            "assignment_completion_percentage": assign_pct
        })

        # Engagement
        engagement_records.append({
            "student_id": s_id,
            "events_attended": events,
            "clubs_participated": clubs,
            "hackathons_participated": hackathons,
            "extracurricular_participation": ec_part,
            "certifications_count": certs
        })

        # Placement
        # Realistic missing values: 6 students (5%) have not completed mock interview yet
        is_mock_missing = (i in [7, 23, 44, 61, 88, 105])
        if is_mock_missing:
            curr_mock = None
            # Normalized composite readiness based on aptitude (40%) and coding (60%)
            readiness = round((0.40 * apt_score + 0.60 * cod_score), 2)
        else:
            curr_mock = mock_score
            # Weighted: 30% Aptitude + 40% Coding + 30% Mock Interview
            readiness = round((0.30 * apt_score + 0.40 * cod_score + 0.30 * curr_mock), 2)

        placement_records.append({
            "student_id": s_id,
            "aptitude_score": apt_score,
            "coding_score": cod_score,
            "mock_interview_score": curr_mock if curr_mock is not None else np.nan,
            "placement_readiness_score": readiness
        })

        # Skills
        skill_sets_by_dept = {
            "Computer Science and Engineering": "Data Structures, Algorithms, Python, System Design, Problem Solving",
            "Information Technology": "Java, Web Development, Database Management, Cloud Basics, Agile",
            "Electronics and Communication Engineering": "Digital Circuits, Microcontrollers, Embedded C, MATLAB, IoT",
            "Data Science": "Python, Machine Learning, SQL, Statistics, Data Visualization",
            "Mechanical Engineering": "CAD Modeling, Thermodynamics, FEA, MATLAB, Project Management"
        }
        # Realistic missing value: 4 students have pending soft skill assessment
        is_soft_skill_missing = (i in [15, 38, 72, 99])
        skills_records.append({
            "student_id": s_id,
            "technical_skill_score": tech_skill,
            "soft_skill_score": np.nan if is_soft_skill_missing else soft_skill,
            "assessed_skills": skill_sets_by_dept[dept],
            "assessment_date": (datetime(2026, 8, 10) + timedelta(days=int(i % 45))).strftime("%Y-%m-%d")
        })

        # Feedback
        # Realistic missing values: 5 students have not filled satisfaction survey yet
        is_feedback_missing = (i in [12, 31, 55, 79, 114])
        feedback_records.append({
            "student_id": s_id,
            "student_satisfaction_score": np.nan if is_feedback_missing else sat_score,
            "faculty_feedback_score": fac_score,
            "feedback_date": (datetime(2026, 9, 1) + timedelta(days=int(i % 30))).strftime("%Y-%m-%d")
        })

    # Save all datasets
    df_academic = pd.DataFrame(academic_records)
    df_academic.to_csv("data/academic.csv", index=False)
    print(f"Generated data/academic.csv ({len(df_academic)} rows)")

    df_attendance = pd.DataFrame(attendance_records)
    df_attendance.to_csv("data/attendance.csv", index=False)
    print(f"Generated data/attendance.csv ({len(df_attendance)} rows)")

    df_lms = pd.DataFrame(lms_records)
    df_lms.to_csv("data/lms_activity.csv", index=False)
    print(f"Generated data/lms_activity.csv ({len(df_lms)} rows)")

    df_engagement = pd.DataFrame(engagement_records)
    df_engagement.to_csv("data/engagement.csv", index=False)
    print(f"Generated data/engagement.csv ({len(df_engagement)} rows)")

    df_placement = pd.DataFrame(placement_records)
    df_placement.to_csv("data/placement.csv", index=False)
    print(f"Generated data/placement.csv ({len(df_placement)} rows)")

    df_skills = pd.DataFrame(skills_records)
    df_skills.to_csv("data/skills.csv", index=False)
    print(f"Generated data/skills.csv ({len(df_skills)} rows)")

    df_feedback = pd.DataFrame(feedback_records)
    df_feedback.to_csv("data/feedback.csv", index=False)
    print(f"Generated data/feedback.csv ({len(df_feedback)} rows)")

    print("\nAll 8 CSV files generated successfully in data/ folder!")

if __name__ == "__main__":
    generate_all_datasets()
