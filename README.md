# Healthcare Worker Training and Scheduling System

## Project Overview

This project is a web application designed to help managers track employee training requirements, monitor deadlines, and schedule training sessions without conflicting with employee work schedules.

The application is being developed using Streamlit, SQLite, and scikit-learn as part of a software development project.

## Team Members:
- Kevin Ruano - Interface Designer
  - Responsible for API specifications and component interface definitions.
- Kyrstin Henderson - Integration Lead
  - Responsible for integrating the AI features with the rest of the application.

Shared Responsibilities: 
- Creating and coordinating system diagrams.

## Tools Used:
- Python
- Streamlit
- SQLite
- Scikit-learn
- GitHub

## Application Features

Our Healthcare Worker Training and Scheduling System helps healthcare managers organize employee information, manage training requirements, and schedule employee shifts.

### Employee Management

The Employee Management page allows managers to:

- View employee information stored in the SQLite database.
- Add new employees.
- Search for employees by name.
- Filter employees by department.
- View employee roles, departments, and email addresses.

### Training Management

The Training Management page allows managers to:

- View available training courses.
- Add new training courses.
- Search and filter training records.
- Track training categories, priorities, and renewal periods.

### Employee Scheduling

The Employee Scheduling page allows managers to:

- Select an employee from the database.
- Assign work shifts using dates and times.
- Save employee schedules.
- View previously saved schedules.
- Prevent overlapping shifts for the same employee.

Employee schedules are stored in SQLite so that saved information remains available after restarting the application.

### AI Training Recommendations

The AI Training Recommendation feature helps managers decide when to assign employee training.

The system uses historical training information and a machine learning model to estimate the probability of an employee completing training on time.

Based on the prediction, the system provides recommendations such as:

- Assign Immediately
- Assign Soon
- Delay Assignment

Managers can review the recommendation before assigning training.

Training assignments are currently saved in a CSV file.

## Installation Instructions

### Requirements

Before running the application, make sure Python is installed on your computer.

### Step 1: Download the Project

Download the repository from GitHub and extract the ZIP file.

Open Command Prompt in the folder containing Home.py and requirements.txt.

### Step 2: Install Dependencies

Run the following command:

```bash
py -m pip install -r requirements.txt
```

### Step 3: Start the Application

Run:

```bash
py -m streamlit run Home.py
```

Streamlit will start the application and provide a local address, usually:

http://localhost:8501

Open that address in your browser.

## Database Information

The application uses SQLite to store employee information and employee work schedules.

The Scheduling page connects to existing employee records, allowing managers to assign shifts without entering employee information again.

Historical training information and training assignments are also maintained in CSV files.

## Automated Testing

The project uses pytest for automated database testing.

To run the tests, open Command Prompt in the project folder and enter:

```bash
py -m pytest -v
```

The current test files include:

- test_database.py
- test_scheduling.py

These tests check:

- Employee table creation.
- Adding employees.
- Duplicate email prevention.
- Employee data persistence.
- Scheduling table creation.
- Saving employee schedules.
- Schedule persistence.
- Employee and schedule database relationships.

Eight automated database tests have passed through GitHub Actions.

The AI recommendation feature does not currently have dedicated automated tests in this test suite.

## Known Limitations

There are still improvements we would like to make in future versions:

- Add support for overnight employee shifts.
- Add automated tests for scheduling conflicts.
- Add automated tests for AI recommendations.
- Improve integration between employee schedules and training assignments.
- Improve how duplicate training assignments are handled.
- Continue improving performance as the amount of data increases.

## Future Improvements

Our goal is to continue improving the system so healthcare managers can organize employee training and work schedules in one application.

Future improvements may include better reporting, more scheduling options, and additional testing.

