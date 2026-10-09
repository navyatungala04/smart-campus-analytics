"""
manage_auth.py
Management utility script for Smart Campus Analytics SQLite user accounts.
Provides CLI commands to initialize demo accounts, add custom accounts,
reset passwords, and verify credentials.
"""

import sys
import os
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth_db import AuthDatabase, DEFAULT_DEMO_PASSWORD

def main():
    parser = argparse.ArgumentParser(description="Smart Campus Analytics Account & Auth Manager")
    parser.add_argument("--init", action="store_true", help="Initialize or sync demo accounts from data/students.csv")
    parser.add_argument("--list", action="store_true", help="List summary of user accounts and featured personas")
    parser.add_argument("--create-user", nargs=4, metavar=("STUDENT_ID", "USERNAME", "PASSWORD", "NAME"),
                        help="Create or update an account: <student_id> <username> <password> <name>")
    parser.add_argument("--reset-password", nargs=2, metavar=("USERNAME_OR_ID", "NEW_PASSWORD"),
                        help="Reset password for an existing account: <username_or_id> <new_password>")
    parser.add_argument("--change-password", nargs=3, metavar=("USERNAME_OR_ID", "CURRENT_PASSWORD", "NEW_PASSWORD"),
                        help="Change password with current verification: <username_or_id> <current_password> <new_password>")
    parser.add_argument("--verify", nargs=2, metavar=("USERNAME_OR_ID", "PASSWORD"),
                        help="Verify login credentials: <username_or_id> <password>")

    args = parser.parse_args()

    auth_db = AuthDatabase()

    if args.init:
        print("[AUTH] Initializing and syncing demo user accounts in SQLite...")
        auth_db._seed_demo_users()
        print("[AUTH] Initialization complete. All student accounts are ready.")

    elif args.list:
        print("=" * 65)
        print("    SMART CAMPUS ANALYTICS - DEMO USER ACCOUNTS SUMMARY")
        print("=" * 65)
        print("\nFeatured Demo Accounts for Testing:")
        print("  1. ⭐ High Achiever:")
        print("     Username: stu1015 (or STU1015)")
        print(f"     Password: {DEFAULT_DEMO_PASSWORD}")
        print("     Student:  Naveen Das (Computer Science, 4th Year)")
        print("\n  2. ⚠️ At-Risk Student:")
        print("     Username: stu1008 (or STU1008)")
        print(f"     Password: {DEFAULT_DEMO_PASSWORD}")
        print("     Student:  Rhea Kumar (ECE, 4th Year)")
        print("\n  3. ⚖️ Steady Performer:")
        print("     Username: stu1002 (or STU1002)")
        print(f"     Password: {DEFAULT_DEMO_PASSWORD}")
        print("     Student:  Surya Kumar (IT, 4th Year)")
        print("\n  4. 💻 Practical Specialist / Hacker:")
        print("     Username: stu1036 (or STU1036)")
        print(f"     Password: {DEFAULT_DEMO_PASSWORD}")
        print("     Student:  Dev Patel (Data Science, 3rd Year)")
        print("-" * 65)
        print(f"Total Student Accounts Available: 120 (usernames: stu1001 to stu1120)")
        print(f"Default Demo Password for All:   {DEFAULT_DEMO_PASSWORD}")
        print("=" * 65)

    elif args.create_user:
        s_id, uname, pwd, name = args.create_user
        res = auth_db.create_user(s_id, uname, pwd, name)
        print(f"[AUTH] Successfully created/updated account:")
        print(f"       Student ID: {res['student_id']}")
        print(f"       Username:   {res['username']}")
        print(f"       Name:       {res['student_name']}")

    elif args.reset_password:
        identifier, new_pwd = args.reset_password
        success = auth_db.reset_password(identifier, new_pwd)
        if success:
            print(f"[AUTH] Successfully reset password for user: {identifier}")
        else:
            print(f"[AUTH ERROR] User '{identifier}' not found in database.")
            sys.exit(1)

    elif args.change_password:
        identifier, curr_p, new_p = args.change_password
        success, msg = auth_db.change_password(identifier, curr_p, new_p)
        if success:
            print(f"[AUTH SUCCESS] {msg} for {identifier}")
        else:
            print(f"[AUTH ERROR] {msg}")
            sys.exit(1)

    elif args.verify:
        identifier, pwd = args.verify
        user = auth_db.authenticate_user(identifier, pwd)
        if user:
            print(f"[AUTH SUCCESS] Credentials valid!")
            print(f"  Student ID:   {user['student_id']}")
            print(f"  Username:     {user['username']}")
            print(f"  Student Name: {user['student_name']}")
        else:
            print(f"[AUTH FAILED] Invalid username or password for: {identifier}")
            sys.exit(1)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
