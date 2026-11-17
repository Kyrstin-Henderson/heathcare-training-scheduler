import streamlit as st
import pandas as pd
import joblib

from datetime import datetime, timedelta
from pathlib import Path

# File Paths
BASE_DIR = Path(__file__).resolve().parent.parent

EMPLOYEE_FILE = BASE_DIR / "data" / "employees.csv"
TRAINING_FILE = BASE_DIR / "data" / "training_data.csv"
HISTORY_FILE = BASE_DIR / "data" / "historical_training_data.csv"

ASSIGNMENT_FILE = (
    BASE_DIR / "data" / "training_assignments.csv"
)

MODEL_FILE = (
    BASE_DIR
    / "models"
    / "training_scheduler_model.pkl"
)

# Page Setup

st.title("AI Training Recommendations")

# Load Data

employees_df = pd.read_csv(EMPLOYEE_FILE)
trainings_df = pd.read_csv(TRAINING_FILE)
history_df = pd.read_csv(HISTORY_FILE)

model = joblib.load(MODEL_FILE)

if "recommendation_generated" not in st.session_state:
    st.session_state["recommendation_generated"] = False

# Employee Selection
employee_options = {
    i + 1: row["name"]
    for i, row in employees_df.iterrows()
}

employee_id = st.selectbox(
    "Select Employee",
    options=list(employee_options.keys()),
    format_func=lambda emp_id: employee_options[emp_id]
)

# Training Selection

training_options = {
    int(row["training_id"]): row["training_name"]
    for _, row in trainings_df.iterrows()
}

training_id = st.selectbox(
    "Select Training",
    options=list(training_options.keys()),
    format_func=lambda t_id: training_options[t_id]
)

current_selection = (
    employee_id,
    training_id
)

if (
    "last_selection" not in st.session_state
    or st.session_state["last_selection"]
        != current_selection
):

    st.session_state["recommendation_generated"] = False

    st.session_state["last_selection"] = current_selection


# Active Training Count
employee_history = history_df[
    history_df["employee_id"] == employee_id
]

active_training_count = len(
    employee_history[
        employee_history["status"].isin(
            ["Pending", "Overdue"]
        )
    ]
)

st.metric(
    "Current Active Trainings",
    active_training_count
)


col1, col2 = st.columns(2)

with col1:
    generate_clicked = st.button(
        "Generate Recommendation"
    )

with col2:
    assign_clicked = st.button(
        "Assign Training"
    )

# Generate AI Recommendation
if generate_clicked:

    probability = model.predict_proba(
        [[
            employee_id,
            training_id,
            active_training_count
        ]]
    )[0][1]

    st.session_state["probability"] = probability
    probability_percent = round(
        probability * 100,
        1
    )



    if probability >= 0.80:

        recommendation = "Assign Immediately"

        st.success(
            f"Recommendation: {recommendation}"
        )

    elif probability >= 0.60:

        recommendation = "Assign Soon"

        st.warning(
            f"Recommendation: {recommendation}"
        )

    else:

        recommendation = "Delay Assignment"

        st.error(
            f"Recommendation: {recommendation}"
        )

    st.session_state["recommendation"] = recommendation
    st.session_state["employee_id"] = employee_id
    st.session_state["training_id"] = training_id
    st.session_state["probability"] = probability
    st.session_state["recommendation_generated"] = True

    if active_training_count >= 5:

        st.info(
            "This employee currently has a high "
            "training workload, which reduces the "
            "predicted likelihood of completing "
            "additional training on time."
        )

    elif probability < 0.60:

        st.info(
            "Historical data indicates employees "
            "with similar training assignments have "
            "frequently completed this training late."
        )

    else:

        st.info(
            "Historical completion patterns suggest "
            "this employee is likely to complete the "
            "training on time."
        )

        st.metric(
            "On-Time Completion Probability",
            f"{probability_percent}%"
        )

# Assign Training
if assign_clicked:

    if not st.session_state["recommendation_generated"]:

        st.warning(
            "Please generate an AI recommendation "
            "before assigning training."
        )

    else:
        if ASSIGNMENT_FILE.exists():

            assignments_df = pd.read_csv(
                ASSIGNMENT_FILE
            )

        else:

            assignments_df = pd.DataFrame(
                columns=[
                    "assignment_id",
                    "employee_id",
                    "training_id",
                    "assigned_date",
                    "due_date",
                    "status"
                ]
            )

        next_id = len(assignments_df) + 1

        assigned_date = datetime.today()

        due_date = assigned_date + timedelta(
            days=60
        )

        new_row = {
            "assignment_id":
                next_id,

            "employee_id":
                st.session_state["employee_id"],

            "training_id":
                st.session_state["training_id"],

            "assigned_date":
                assigned_date.strftime(
                    "%Y-%m-%d"
                ),

            "due_date":
                due_date.strftime(
                    "%Y-%m-%d"
                ),
            "status":
                "Pending"
       }

        assignments_df = pd.concat(
            [
                assignments_df,
                pd.DataFrame([new_row])
            ],
            ignore_index=True
        )

        assignments_df.to_csv(
            ASSIGNMENT_FILE,
            index=False
        )

        st.success(
            "Training assigned successfully!"
        )

        st.write(
            f"Employee: "
            f"{employee_options[st.session_state['employee_id']]}"
        )

        st.write(
            f"Training: "
            f"{training_options[st.session_state['training_id']]}"
        )

# Upcoming Training Assignments
st.subheader("Upcoming Training Assignments")

if ASSIGNMENT_FILE.exists():

    assignments_df = pd.read_csv(
        ASSIGNMENT_FILE
    )

    if not assignments_df.empty:

        display_df = assignments_df.copy()

        display_df["Employee"] = (
            display_df["employee_id"]
            .apply(
                lambda x: employee_options.get(
                    x,
                    "Unknown"
                )
            )
        )

        display_df["Training"] = (
            display_df["training_id"]
            .apply(
                lambda x: training_options.get(
                    x,
                    "Unknown"
                )
            )
        )

        display_df = display_df[
            [
                "Employee",
                "Training",
                "assigned_date",
                "due_date",
                "status"
            ]
        ]

        display_df.columns = [
            "Employee",
            "Training",
            "Assigned Date",
            "Due Date",
            "Status"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No training assignments have been created yet."
        )

else:

    st.info(
        "No training assignments have been created yet."
    )