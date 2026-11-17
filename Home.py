from pathlib import Path
import streamlit as st

from database.db_setup import create_tables
from scripts.generate_training_history import generate_data


def initialize_system():
    """Initialize application resources."""

    create_tables()

    history_file = Path("data/historical_training_data.csv")

    if not history_file.exists() or history_file.stat().st_size == 0:
        generate_data()


initialize_system()

# Configure Streamlit page
st.set_page_config(
    page_title="Healthcare Training Scheduler",
    page_icon="",
    layout="wide"
)

# Dashboard
st.title("Healthcare Training Scheduler")

st.markdown("""
Welcome to the Healthcare Training Scheduler.

This system helps healthcare organizations:

- Manage employee training requirements
- Track compliance and due dates
- Schedule upcoming training sessions
- Identify overdue certifications
- Generate AI-powered scheduling recommendations
""")

import pandas as pd

employees = pd.read_csv("data/employees.csv")
trainings = pd.read_csv("data/training_data.csv")
history = pd.read_csv("data/historical_training_data.csv")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Employees", len(employees))

with col2:
    st.metric("Training Courses", len(trainings))

with col3:
    st.metric("Historical Records", len(history))

st.divider()

st.subheader("Navigation")

st.info(
    """
    Use the left sidebar to navigate between:
    
    • Employees
    
    • Training
    
    • Scheduling
    
    • AI Recommendations
    """
)