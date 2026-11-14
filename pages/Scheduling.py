import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


# Database location
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "database.db"


# Connect to SQLite database
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create scheduling table
def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
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


# Get existing employees
def get_employees():
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT id, name, role, department
            FROM employees
            ORDER BY name
            """,
            conn
        )


# Save a new employee schedule
def add_schedule(employee_id, shift_date, start_time, end_time, department):

    with get_connection() as conn:

        # Prevent overlapping shifts for the same employee
        conflict = conn.execute(
            """
            SELECT COUNT(*)
            FROM schedules
            WHERE employee_id = ?
              AND shift_date = ?
              AND start_time < ?
              AND end_time > ?
            """,
            (
                employee_id,
                shift_date,
                end_time,
                start_time
            )
        ).fetchone()[0]

        if conflict > 0:
            return False

        conn.execute(
            """
            INSERT INTO schedules (
                employee_id,
                shift_date,
                start_time,
                end_time,
                department
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                shift_date,
                start_time,
                end_time,
                department
            )
        )

    return True


# Retrieve saved schedules
def get_schedules():
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT
                s.shift_date AS Date,
                e.name AS Employee,
                e.role AS Role,
                s.department AS Department,
                s.start_time AS Start,
                s.end_time AS End
            FROM schedules s
            JOIN employees e
                ON s.employee_id = e.id
            ORDER BY s.shift_date, s.start_time
            """,
            conn
        )


# Initialize scheduling database
initialize_database()


# Application heading
st.title("Employee Scheduling")
st.write("Manage healthcare employee shifts and work schedules.")


# Load employee information
try:
    employees = get_employees()
except sqlite3.Error:
    st.error("Could not load employees from the database.")
    st.stop()


# Add employee schedule
st.subheader("Assign Employee Shift")

if employees.empty:
    st.warning("Please add employees before creating schedules.")

else:

    with st.form("schedule_form"):

        employee_options = {
            int(row["id"]): f"{row['name']} - {row['role']}"
            for _, row in employees.iterrows()
        }

        employee_id = st.selectbox(
            "Select Employee",
            options=list(employee_options.keys()),
            format_func=lambda emp_id: employee_options[emp_id]
        )

        shift_date = st.date_input("Shift Date")

        start_time = st.time_input(
            "Start Time",
            value=datetime.strptime("08:00", "%H:%M").time()
        )

        end_time = st.time_input(
            "End Time",
            value=datetime.strptime("16:00", "%H:%M").time()
        )

        selected_employee = employees[
            employees["id"] == employee_id
        ].iloc[0]

        department = selected_employee["department"]

        st.write(f"Department: {department}")

        submitted = st.form_submit_button("Save Schedule")

        if submitted:

            if end_time <= start_time:
                st.error("End time must be later than start time.")

            else:
                try:
                    saved = add_schedule(
                        employee_id,
                        shift_date.isoformat(),
                        start_time.strftime("%H:%M"),
                        end_time.strftime("%H:%M"),
                        department
                    )

                    if saved:
                        st.success("Employee schedule saved successfully!")

                    else:
                        st.error(
                            "Scheduling conflict! This employee "
                            "already has an overlapping shift."
                        )

                except sqlite3.Error:
                    st.error("Could not save schedule. Please try again.")


# Display employee schedules
st.subheader("Employee Schedule List")

try:
    schedules = get_schedules()

    if not schedules.empty:

        st.dataframe(
            schedules,
            width="stretch",
            hide_index=True
        )

    else:
        st.info("No employee schedules have been created yet.")

except sqlite3.Error:
    st.error("Could not load employee schedules.")
