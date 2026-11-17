import joblib

model = joblib.load(
    "training_scheduler_model.pkl"
)

def get_recommendation(
    employee_id,
    training_id,
    active_training_count
):

    probability = model.predict_proba(
        [[
            employee_id,
            training_id,
            active_training_count
        ]]
    )[0][1]

    if probability >= 0.8:
        recommendation = "Assign Immediately"

    elif probability >= 0.6:
        recommendation = "Assign Soon"

    else:
        recommendation = "Delay Assignment"

    return {
        "probability": round(
            probability * 100,
            1
        ),
        "recommendation": recommendation
    }

print(
    get_recommendation(
        employee_id=1,
        training_id=5,
        active_training_count=2
    )
)