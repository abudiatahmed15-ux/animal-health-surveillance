import joblib
import pandas as pd


MODEL_PATH = "ai/models/livestock_disease_model.joblib"


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_disease(animal_data):

    # Convert input dictionary into a DataFrame
    input_df = pd.DataFrame([animal_data])

    # Predict disease
    prediction = model.predict(input_df)[0]

    # Get prediction probabilities
    probabilities = model.predict_proba(input_df)[0]

    # Get all disease classes
    classes = model.classes_

    # Find highest probability
    confidence = probabilities.max()

    return {
        "predicted_disease": prediction,
        "confidence": confidence
    }


# ============================================================
# TEST INPUT
# ============================================================

sample_animal = {
    "Animal_Type": "Cow",
    "Breed": "Jersey",
    "Gender": "Female",

    "Symptom_1": "Fever",
    "Symptom_2": "Coughing",
    "Symptom_3": "Nasal Discharge",
    "Symptom_4": "Loss of Appetite",

    "Duration": 5,

    "Age": 4,
    "Weight": 350,

    "Body_Temperature": 40.0,
    "Heart_Rate": 90,

    "Appetite_Loss": 1,
    "Vomiting": 0,
    "Diarrhea": 0,
    "Coughing": 1,
    "Labored_Breathing": 1,
    "Lameness": 0,
    "Skin_Lesions": 0,
    "Nasal_Discharge": 1,
    "Eye_Discharge": 0
}


# ============================================================
# RUN TEST
# ============================================================

result = predict_disease(sample_animal)


print("\n===== CLINICAL DISEASE PREDICTION =====")

print(
    "Predicted Disease:",
    result["predicted_disease"]
)

print(
    "Confidence:",
    round(result["confidence"] * 100, 2),
    "%"
)