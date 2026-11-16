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

def import_employees_from_csv():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "employees.csv"

    employees = pd.read_csv(csv_path)

    with get_connection() as conn:
        for _, row in employees.iterrows():
            try:
                conn.execute(
                    """
                    INSERT INTO employees
                    (name, role, department, email)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        row["name"],
                        row["role"],
                        row["department"],
                        row["email"],
                    ),
                )
            except sqlite3.IntegrityError:
                pass


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

count = pd.read_sql_query(
    "SELECT COUNT(*) AS count FROM employees",
    get_connection()
)

if count.iloc[0]["count"] == 0:
    import_employees_from_csv()

st.title("Employee Management")
st.write("Manage healthcare employees and their information.")

st.subheader("Add New Employee")

with st.form("employee_form"):
    name = st.text_input("Employee Name")
    role = st.selectbox(
        "Job Role",
        ["Registered Nurse", "Physician", "Lab Technician", "Radiology Technician", "Other"]
    )
    department = st.selectbox(
        "Department",
        ["Emergency", "Surgery", "Pediatrics", "Administration", "Radiology", "ICU", "Laboratory", "Cardiology", "Other"]
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

st.subheader(f"Employee List - {count.iloc[0]['count']} Employees")

try:
    employees = get_employees()

    if not employees.empty:
        search = st.text_input("Search Employee")

        department_filter = st.selectbox(
            "Department",
            ["All"] + sorted(employees["Department"].unique().tolist())
        )

        filtered_employees = employees.copy()

        if search:
            filtered_employees = filtered_employees[
                filtered_employees["Name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if department_filter != "All":
            filtered_employees = filtered_employees[
                filtered_employees["Department"] == department_filter
            ]

        filtered_employees.index = range(1, len(filtered_employees) + 1)
        filtered_employees.index.name = "Employee #"

        st.dataframe(
            filtered_employees,
            use_container_width=True
        )
    else:
        st.info("No employees have been added yet.")
except sqlite3.Error:
    st.error("Could not load employee records.")
