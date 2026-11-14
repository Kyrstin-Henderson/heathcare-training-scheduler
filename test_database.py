import sqlite3

import pytest

from database import db_setup


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    # Use a separate database for testing
    database_path = tmp_path / "test_database.db"

    monkeypatch.setattr(db_setup, "DB_PATH", database_path)

    # Create the employee table
    db_setup.create_tables()

    return database_path


def test_employee_table_created(test_database):
    # Check that the employees table exists
    with sqlite3.connect(test_database) as conn:
        result = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'employees'
            """
        ).fetchone()

    assert result is not None


def test_add_employee(test_database):
    # Test saving an employee
    with sqlite3.connect(test_database) as conn:
        conn.execute(
            """
            INSERT INTO employees (name, role, department, email)
            VALUES (?, ?, ?, ?)
            """,
            ("Alex Johnson", "Nurse", "Emergency", "alex@example.com")
        )

    # Verify the employee was saved
    with sqlite3.connect(test_database) as conn:
        result = conn.execute(
            "SELECT name FROM employees WHERE email = ?",
            ("alex@example.com",)
        ).fetchone()

    assert result[0] == "Alex Johnson"


def test_duplicate_email(test_database):
    # Add the first employee
    with sqlite3.connect(test_database) as conn:
        conn.execute(
            """
            INSERT INTO employees (name, role, department, email)
            VALUES (?, ?, ?, ?)
            """,
            ("Alex Johnson", "Nurse", "Emergency", "alex@example.com")
        )

    # Check that SQLite rejects a duplicate email
    with pytest.raises(sqlite3.IntegrityError):
        with sqlite3.connect(test_database) as conn:
            conn.execute(
                """
                INSERT INTO employees (name, role, department, email)
                VALUES (?, ?, ?, ?)
                """,
                ("Alex Johnson", "Nurse", "Emergency", "alex@example.com")
            )


def test_employee_persistence(test_database):
    # Save an employee
    with sqlite3.connect(test_database) as conn:
        conn.execute(
            """
            INSERT INTO employees (name, role, department, email)
            VALUES (?, ?, ?, ?)
            """,
            ("Maria Lopez", "Nurse", "Surgery", "maria@example.com")
        )

    # Reopen database and verify employee still exists
    with sqlite3.connect(test_database) as conn:
        result = conn.execute(
            "SELECT name FROM employees WHERE email = ?",
            ("maria@example.com",)
        ).fetchone()

    assert result[0] == "Maria Lopez"
