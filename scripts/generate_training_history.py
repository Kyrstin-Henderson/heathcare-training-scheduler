import csv
import random
from datetime import datetime, timedelta
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent

EMPLOYEE_FILE = BASE_DIR / "data" / "employees.csv"
TRAINING_FILE = BASE_DIR / "data" / "training_data.csv"
OUTPUT_FILE = BASE_DIR / "data" / "historical_training_data.csv"

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = BASE_DIR / "data" / "historical_training_data.csv"
random.seed(42)


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


employees = load_csv(EMPLOYEE_FILE)
trainings = load_csv(TRAINING_FILE)

training_lookup = {
    int(t["training_id"]): t
    for t in trainings
}

# Role-specific training recommendations
ROLE_TRAININGS = {
    "Registered Nurse": [1, 2, 3, 4, 5, 7, 9, 13, 14, 15],
    "Physician": [1, 2, 3, 5, 9, 13, 15],
    "Respiratory Therapist": [1, 2, 3, 4, 7, 13],
    "Radiology Technician": [1, 3, 4, 8, 10],
    "Lab Technician": [1, 3, 7, 10, 15],
    "Pharmacist": [1, 5, 8, 9, 15],
    "Medical Assistant": [1, 3, 5, 8, 14],
    "Physical Therapist": [1, 3, 6, 14],
    "Department Manager": [1, 4, 5, 6, 11, 12],
}

records = []
record_id = 1

today = datetime.today()

for employee_id, employee in enumerate(employees, start=1):

    role = employee["role"]

    employee_trainings = ROLE_TRAININGS.get(
        role,
        [1, 3, 5, 11, 12]
    )

    for year in range(2022, 2027):

        for training_id in employee_trainings:

            assigned_date = datetime(
                year,
                random.randint(1, 10),
                random.randint(1, 28)
            )

            due_date = assigned_date + timedelta(days=60)

            # Historical years = completed
            if year < 2026:

                completion_offset = random.randint(-20, 25)

                completion_date = due_date + timedelta(
                    days=completion_offset
                )

                status = (
                    "Completed"
                    if completion_offset <= 0
                    else "Completed Late"
                )

            else:

                chance = random.random()

                if chance < 0.60:
                    completion_offset = random.randint(-20, 10)

                    completion_date = due_date + timedelta(
                        days=completion_offset
                    )

                    status = (
                        "Completed"
                        if completion_offset <= 0
                        else "Completed Late"
                    )

                elif chance < 0.85:
                    completion_date = ""

                    status = "Pending"

                else:
                    completion_date = ""

                    status = "Overdue"

            days_early_late = ""

            if completion_date and isinstance(completion_date, datetime):
                days_early_late = (
                    due_date - completion_date
                ).days

                completion_date = (
                    completion_date.strftime("%Y-%m-%d")
                )

            records.append(
                {
                    "record_id": record_id,
                    "employee_id": employee_id,
                    "training_id": training_id,
                    "assigned_date":
                        assigned_date.strftime("%Y-%m-%d"),
                    "due_date":
                        due_date.strftime("%Y-%m-%d"),
                    "completion_date":
                        completion_date,
                    "status":
                        status,
                    "days_early_late":
                        days_early_late,
                }
            )

            record_id += 1

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    fieldnames = [
        "record_id",
        "employee_id",
        "training_id",
        "assigned_date",
        "due_date",
        "completion_date",
        "status",
        "days_early_late",
    ]

    writer = csv.DictWriter(
        csvfile,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(records)

print(
    f"Generated {len(records)} records "
    f"into {OUTPUT_FILE.name}"
)