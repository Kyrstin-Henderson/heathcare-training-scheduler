
import streamlit as st
import pandas as pd

st.title("Employee Management")
st.write("Manage healthcare employees and their information.")

# Store employees during the current session
if "employees" not in st.session_state:
    st.session_state.employees = []

# Form to add employees
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
            employee = {
                "Name": name.strip(),
                "Role": role,
                "Department": department,
                "Email": email.strip()
            }

            st.session_state.employees.append(employee)
            st.success("Employee added successfully!")

# Display employees
st.subheader("Employee List")

if st.session_state.employees:
    employee_df = pd.DataFrame(st.session_state.employees)
    st.dataframe(employee_df, use_container_width=True)
else:
    st.info("No employees have been added yet.")
