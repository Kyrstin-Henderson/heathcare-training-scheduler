import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

# Database location
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "database.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)


def add_employee(name, role, department, email):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO employees (name, role, department, email)
            VALUES (?, ?, ?, ?)
            """,
            (name, role, department, email)
        )


def get_employees():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT name AS Name, role AS Role, "
            "department AS Department, email AS Email "
            "FROM employees ORDER BY id",
            conn
        )


# Create the employee table if needed
initialize_database()

st.title("Employee Management")
st.write("Manage healthcare employees and their information.")

st.subheader("Add New Employee")

with st.form("employee_form"):
    name = st.text_input("Employee Name")
    role = st.selectbox(
        "Job Role",
        ["Nurse", "Doctor", "Medical Assistant", "Technician", "Other"]
    )
    department = st.selectbox(
        "Department",
        ["Emergency", "Surgery", "Pediatrics", "General", "Other"]
    )
    email = st.text_input("Email Address")

    submitted = st.form_submit_button("Add Employee")

    if submitted:
        if not name.strip() or not email.strip():
            st.error("Please enter a name and email address.")
        elif "@" not in email:
            st.error("Please enter a valid email address.")
        else:
            try:
                add_employee(
                    name.strip(),
                    role,
                    department,
                    email.strip()
                )
                st.success("Employee added successfully!")
            except sqlite3.IntegrityError:
                st.error("An employee with this email already exists.")
            except sqlite3.Error:
                st.error("Could not save employee. Please try again.")

st.subheader("Employee List")

try:
    employees = get_employees()

    if not employees.empty:
        st.dataframe(employees, use_container_width=True)
    else:
        st.info("No employees have been added yet.")
except sqlite3.Error:
    st.error("Could not load employee records.")
