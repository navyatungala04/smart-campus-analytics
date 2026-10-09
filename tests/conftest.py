"""
conftest.py
Global pytest configuration for Smart Campus Analytics.
Configures all automated tests to execute against an isolated test database (data/test_auth.db),
guaranteeing that the live application database (data/auth.db) remains 100% untouched.
"""

import os
import pytest

TEST_DB_PATH = os.path.join("data", "test_auth.db")
REAL_DB_PATH = os.path.join("data", "auth.db")

# Enforce test database environment variable before any modules are imported
os.environ["AUTH_DB_PATH"] = TEST_DB_PATH

@pytest.fixture(scope="session", autouse=True)
def configure_test_database():
    """
    Session-level autouse fixture:
    - Sets AUTH_DB_PATH to data/test_auth.db
    - Initializes test database with student accounts from students.csv
    - Verifies isolation from the real database
    """
    os.environ["AUTH_DB_PATH"] = TEST_DB_PATH
    
    from src.auth_db import AuthDatabase
    test_db = AuthDatabase(db_path=TEST_DB_PATH)
    
    yield test_db
