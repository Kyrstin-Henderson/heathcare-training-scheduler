import sqlite3

import pytest


@pytest.fixture
def test_database(tmp_path):
    # Create a separate database for testing
    database_path = tmp_path / "test_scheduling.db"

    with sqlite3.connect(database_path) as conn:

        conn.execute("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                shift_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                department TEXT NOT NULL,
                FOREIGN KEY (employee_id)
                    REFERENCES employees(id)
            )
        """)

        conn.execute("""
            INSERT INTO employees
            VALUES (1, 'Aaron Collins', 'Registered Nurse',
                    'Surgery', 'aaron@example.com')
        """)

    return database_path


def test_schedule_table_created(test_database):
    # Check that the scheduling table exists
    with sqlite3.connect(test_database) as conn:
        result = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'schedules'
            """
        ).fetchone()

    assert result is not None


def test_add_schedule(test_database):
    # Test saving an employee shift
    with sqlite3.connect(test_database) as conn:
        conn.execute(
            """
            INSERT INTO schedules
            (employee_id, shift_date, start_time, end_time, department)
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, "2026-11-16", "08:00", "16:00", "Surgery")
        )

    with sqlite3.connect(test_database) as conn:
        result = conn.execute(
            "SELECT shift_date FROM schedules WHERE employee_id = 1"
        ).fetchone()

    assert result[0] == "2026-11-16"


def test_schedule_persistence(test_database):
    # Save a shift to the database
    with sqlite3.connect(test_database) as conn:
        conn.execute(
            """
            INSERT INTO schedules
            (employee_id, shift_date, start_time, end_time, department)
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, "2026-11-16", "08:00", "16:00", "Surgery")
        )

    # Reopen database to verify the shift remains
    with sqlite3.connect(test_database) as conn:
        result = conn.execute(
            "SELECT COUNT(*) FROM schedules"
        ).fetchone()

    assert result[0] == 1


def test_employee_schedule_relationship(test_database):
    # Verify schedules connect to employees
    with sqlite3.connect(test_database) as conn:
        conn.execute(
            """
            INSERT INTO schedules
            (employee_id, shift_date, start_time, end_time, department)
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, "2026-11-16", "08:00", "16:00", "Surgery")
        )

    with sqlite3.connect(test_database) as conn:
        result = conn.execute(
            """
            SELECT employees.name
            FROM schedules
            JOIN employees
                ON schedules.employee_id = employees.id
            """
        ).fetchone()

    assert result[0] == "Aaron Collins"
