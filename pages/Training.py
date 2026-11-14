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
            CREATE TABLE IF NOT EXISTS trainings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                training_name TEXT NOT NULL,
                duration_hours INTEGER NOT NULL,
                category TEXT NOT NULL,
                renewal_period_days INTEGER NOT NULL,
                priority TEXT NOT NULL
            )
        """)

def import_trainings_from_csv():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "training_data.csv"

    trainings = pd.read_csv(csv_path)

    with get_connection() as conn:
        for _, row in trainings.iterrows():
            try:
                conn.execute(
                    """
                    INSERT INTO trainings
                    (training_name, duration_hours, category, renewal_period_days, priority)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        row["training_name"],
                        row["duration_hours"],
                        row["category"],
                        row["renewal_period_days"],
                        row["priority"],
                    ),
                )
            except sqlite3.IntegrityError:
                pass

def add_training(
    training_name,
    duration_hours,
    category,
    renewal_period_days,
    priority
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO trainings (
                training_name,
                duration_hours,
                category,
                renewal_period_days,
                priority
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                training_name,
                duration_hours,
                category,
                renewal_period_days,
                priority
            )
        )


def get_trainings():
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT
                training_name AS Training,
                category AS Category,
                priority AS Priority,
                duration_hours AS Hours,
                renewal_period_days AS Renewal_Days
            FROM trainings
            ORDER BY id
            """,
            conn
        )


# Create table if needed
initialize_database()

count = pd.read_sql_query(
    "SELECT COUNT(*) AS count FROM trainings",
    get_connection()
)

if count.iloc[0]["count"] == 0:
    import_trainings_from_csv()

st.title("Training Management")
st.write("Manage training courses and requirements.")

# ------------------------
# Add Training Form
# ------------------------

st.subheader("Add New Training")

with st.form("training_form"):

    training_name = st.text_input("Training Name")

    duration_hours = st.number_input(
        "Duration (Hours)",
        min_value=1,
        max_value=40,
        value=2
    )

    category = st.selectbox(
        "Category",
        [
            "Compliance",
            "Clinical",
            "Safety",
            "Technology",
            "Documentation",
            "Patient Safety"
        ]
    )

    renewal_period_days = st.number_input(
        "Renewal Period (Days)",
        min_value=30,
        max_value=3650,
        value=365
    )

    priority = st.selectbox(
        "Priority",
        ["High", "Medium", "Low"]
    )

    submitted = st.form_submit_button("Add Training")

    if submitted:

        if not training_name.strip():

            st.error("Please enter a training name.")

        else:

            try:

                add_training(
                    training_name.strip(),
                    duration_hours,
                    category,
                    renewal_period_days,
                    priority
                )

                st.success("Training added successfully!")

            except sqlite3.Error:

                st.error(
                    "Could not save training."
                )

# ------------------------
# Display Trainings
# ------------------------

st.subheader("Training Catalog")

try:

    trainings = get_trainings()

    if not trainings.empty:

        # Metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Trainings",
                len(trainings)
            )

        with col2:
            st.metric(
                "Categories",
                trainings["Category"].nunique()
            )

        with col3:
            st.metric(
                "High Priority",
                len(
                    trainings[
                        trainings["Priority"] == "High"
                    ]
                )
            )

        st.divider()

        # Search
        search = st.text_input(
            "Search Trainings"
        )

        category_filter = st.selectbox(
            "Category Filter",
            ["All"]
            + sorted(
                trainings["Category"]
                .unique()
                .tolist()
            )
        )

        filtered = trainings.copy()

        if search:

            filtered = filtered[
                filtered["Training"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if category_filter != "All":

            filtered = filtered[
                filtered["Category"]
                == category_filter
            ]

        filtered.index = range(
            1,
            len(filtered) + 1
        )

        filtered.index.name = "#"

        st.dataframe(
            filtered,
            use_container_width=True
        )

    else:

        st.info(
            "No trainings have been added yet."
        )

except sqlite3.Error:

    st.error(
        "Could not load training records."
    )