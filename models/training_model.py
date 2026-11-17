import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

print("Starting model training...")
# Load data
df = pd.read_csv("../data/historical_training_data.csv")

# Only use completed records
df = df[
    df["status"].isin([
        "Completed",
        "Completed Late"
    ])
]

# Target
df["on_time_completion"] = (
    df["status"] == "Completed"
).astype(int)

# Features
X = df[
    [
        "employee_id",
        "training_id",
        "active_training_count"
    ]
]

y = df["on_time_completion"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)

print(f"Accuracy: {accuracy:.2f}")

# Save model
joblib.dump(
    model,
    "training_scheduler_model.pkl"
)

print("Model saved!")
