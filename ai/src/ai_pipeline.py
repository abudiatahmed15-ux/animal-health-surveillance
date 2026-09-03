import pandas as pd
import joblib

from case_assessment import assess_case


# =========================================================
# MODEL PATH
# =========================================================

MODEL_PATH = "ai/models/livestock_disease_model.joblib"


# =========================================================
# LOAD MODEL
# =========================================================

print("\nLoading clinical ML model...")

model = joblib.load(MODEL_PATH)

print("ML model loaded successfully.")


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def convert_binary(value):

    if value is None:
        return 0

    text = str(value).strip().lower()

    if text in ["yes", "true", "1"]:
        return 1

    if text in ["no", "false", "0"]:
        return 0

    return 0


def convert_number(value):

    try:
        return float(value)

    except (ValueError, TypeError):
        return 0.0


# =========================================================
# CLINICAL ML PREDICTION
# =========================================================

def clinical_ml_prediction(case):

    data = {

        "Animal_Type":
            case.get("Animal_Type"),

        "Breed":
            case.get("Breed"),

        "Age":
            convert_number(case.get("Age")),

        "Gender":
            case.get("Gender"),

        "Weight":
            convert_number(case.get("Weight")),

        "Symptom_1":
            case.get("Symptom_1"),

        "Symptom_2":
            case.get("Symptom_2"),

        "Symptom_3":
            case.get("Symptom_3"),

        "Symptom_4":
            case.get("Symptom_4"),

        "Duration":
            case.get("Duration"),

        "Appetite_Loss":
            convert_binary(case.get("Appetite_Loss")),

        "Vomiting":
            convert_binary(case.get("Vomiting")),

        "Diarrhea":
            convert_binary(case.get("Diarrhea")),

        "Coughing":
            convert_binary(case.get("Coughing")),

        "Labored_Breathing":
            convert_binary(case.get("Labored_Breathing")),

        "Lameness":
            convert_binary(case.get("Lameness")),

        "Skin_Lesions":
            convert_binary(case.get("Skin_Lesions")),

        "Nasal_Discharge":
            convert_binary(case.get("Nasal_Discharge")),

        "Eye_Discharge":
            convert_binary(case.get("Eye_Discharge")),

        "Body_Temperature":
            convert_number(case.get("Body_Temperature")),

        "Heart_Rate":
            convert_number(case.get("Heart_Rate"))
    }


    feature_columns = [

        "Animal_Type",
        "Breed",
        "Age",
        "Gender",
        "Weight",

        "Symptom_1",
        "Symptom_2",
        "Symptom_3",
        "Symptom_4",

        "Duration",

        "Appetite_Loss",
        "Vomiting",
        "Diarrhea",
        "Coughing",
        "Labored_Breathing",
        "Lameness",
        "Skin_Lesions",
        "Nasal_Discharge",
        "Eye_Discharge",

        "Body_Temperature",
        "Heart_Rate"
    ]


    X = pd.DataFrame(
        [data],
        columns=feature_columns
    )


    # -----------------------------------------------------
    # ML PREDICTION
    # -----------------------------------------------------

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    classes = model.classes_

    best_index = probabilities.argmax()

    confidence = probabilities[best_index]


    # -----------------------------------------------------
    # TOP 3
    # -----------------------------------------------------

    top_indices = probabilities.argsort()[-3:][::-1]

    top_predictions = []

    for index in top_indices:

        top_predictions.append({

            "disease":
                classes[index],

            "confidence":
                round(
                    probabilities[index] * 100,
                    2
                )
        })


    # -----------------------------------------------------
    # FMD ML CONFIDENCE
    # -----------------------------------------------------

    fmd_ml_confidence = 0.0

    for index, disease in enumerate(classes):

        if disease == "Foot-and-Mouth Disease":

            fmd_ml_confidence = (
                probabilities[index] * 100
            )

            break


    return {

        "prediction":
            prediction,

        "confidence":
            round(
                confidence * 100,
                2
            ),

        "fmd_ml_confidence":
            round(
                fmd_ml_confidence,
                2
            ),

        "top_predictions":
            top_predictions
    }


# =========================================================
# EXPLAINABLE SURVEILLANCE SCORE
# =========================================================

def calculate_surveillance_score(
    ml_result,
    surveillance_result
):

    # -----------------------------------------------------
    # COMPONENT 1
    # FMD CLINICAL SCREENING
    # -----------------------------------------------------

    fmd_score = surveillance_result["fmd_score"]

    clinical_component = (
        fmd_score * 0.50
    )


    # -----------------------------------------------------
    # COMPONENT 2
    # HISTORICAL RISK
    # -----------------------------------------------------

    historical_risk = surveillance_result[
        "historical_risk"
    ]

    historical_component = (
        min(historical_risk, 100) * 0.20
    )


    # -----------------------------------------------------
    # COMPONENT 3
    # DISTRICT FORECAST
    # -----------------------------------------------------

    district_forecast = surveillance_result[
        "district_forecast"
    ]

    if district_forecast != "NONE":

        forecast_component = 30

    else:

        forecast_component = 0


    # -----------------------------------------------------
    # COMPONENT 4
    # ML SUPPORT
    # -----------------------------------------------------

    fmd_ml_confidence = ml_result[
        "fmd_ml_confidence"
    ]

    ml_component = (
        fmd_ml_confidence * 0.10
    )


    # -----------------------------------------------------
    # TOTAL
    # -----------------------------------------------------

    total_score = (
        clinical_component
        + historical_component
        + forecast_component
        + ml_component
    )

    total_score = min(
        round(total_score, 2),
        100
    )


    # -----------------------------------------------------
    # PRIORITY
    # -----------------------------------------------------

    if total_score >= 75:

        priority = "URGENT"

    elif total_score >= 50:

        priority = "HIGH"

    elif total_score >= 25:

        priority = "MEDIUM"

    else:

        priority = "ROUTINE"


    # -----------------------------------------------------
    # EXPLANATION
    # -----------------------------------------------------

    reasons = []


    if fmd_score >= 60:

        reasons.append(
            "Strong FMD-specific clinical surveillance signal"
        )

    elif fmd_score >= 35:

        reasons.append(
            "Moderate FMD clinical surveillance signal"
        )


    if historical_risk >= 50:

        reasons.append(
            "High historical FMD risk in Maharashtra data"
        )

    elif historical_risk >= 25:

        reasons.append(
            "Moderate historical FMD risk in Maharashtra data"
        )

    elif historical_risk > 0:

        reasons.append(
            "Historical FMD activity is present in the surveillance data"
        )


    if district_forecast != "NONE":

        reasons.append(
            "District appears in the available FMD risk forecast"
        )


    if fmd_ml_confidence >= 50:

        reasons.append(
            "Clinical ML model provides additional FMD support"
        )

    elif ml_result["prediction"] != "Foot-and-Mouth Disease":

        reasons.append(
            "Clinical ML prediction does not independently confirm FMD"
        )


    return {

        "surveillance_score":
            total_score,

        "priority":
            priority,

        "reasons":
            reasons,

        "components": {

            "clinical_screening":
                round(clinical_component, 2),

            "historical_risk":
                round(historical_component, 2),

            "district_forecast":
                round(forecast_component, 2),

            "ml_support":
                round(ml_component, 2)
        }
    }


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    print("\n==============================================")
    print("       AI ANIMAL HEALTH SURVEILLANCE")
    print("==============================================")


    # =====================================================
    # DEMO CASE
    # =====================================================

    case = {

        "Animal_Type": "Cow",

        "Breed": "Gir",

        "Age": 4,

        "Gender": "Female",

        "Weight": 350,

        "Symptom_1": "Fever",

        "Symptom_2": "Mouth lesions",

        "Symptom_3": "Lameness",

        "Symptom_4": "Excessive salivation",

        "Duration": "5 days",

        "Appetite_Loss": "Yes",

        "Vomiting": "No",

        "Diarrhea": "No",

        "Coughing": "No",

        "Labored_Breathing": "No",

        "Lameness": "Yes",

        "Skin_Lesions": "No",

        "Nasal_Discharge": "No",

        "Eye_Discharge": "No",

        "Body_Temperature": 40.2,

        "Heart_Rate": 90,

        "District": "Ahmadnagar"
    }


    # =====================================================
    # CLINICAL ML
    # =====================================================

    print("\n--- CLINICAL ML MODEL ---")

    ml_result = clinical_ml_prediction(case)

    print(
        "Predicted disease:",
        ml_result["prediction"]
    )

    print(
        "Model confidence:",
        f'{ml_result["confidence"]}%'
    )

    print(
        "FMD ML confidence:",
        f'{ml_result["fmd_ml_confidence"]}%'
    )

    print("\nTop 3 predictions:")

    for item in ml_result["top_predictions"]:

        print(
            f'  {item["disease"]}: '
            f'{item["confidence"]}%'
        )


    # =====================================================
    # MAHARASHTRA SURVEILLANCE
    # =====================================================

    print("\n--- MAHARASHTRA SURVEILLANCE ---")

    surveillance_result = assess_case(case)

    print(
        "FMD surveillance flag:",
        surveillance_result["fmd_flag"]
    )

    print(
        "FMD surveillance score:",
        surveillance_result["fmd_score"]
    )

    print(
        "FMD surveillance risk:",
        surveillance_result["fmd_risk"]
    )

    print(
        "Historical FMD risk:",
        surveillance_result["historical_risk"]
    )

    print(
        "District forecast:",
        surveillance_result["district_forecast"]
    )


    # =====================================================
    # EXPLAINABLE SCORE
    # =====================================================

    print("\n--- EXPLAINABLE SURVEILLANCE SCORE ---")

    score_result = calculate_surveillance_score(
        ml_result,
        surveillance_result
    )

    print(
        "Clinical screening contribution:",
        score_result["components"]["clinical_screening"]
    )

    print(
        "Historical risk contribution:",
        score_result["components"]["historical_risk"]
    )

    print(
        "District forecast contribution:",
        score_result["components"]["district_forecast"]
    )

    print(
        "ML support contribution:",
        score_result["components"]["ml_support"]
    )

    print(
        "\nOverall surveillance score:",
        score_result["surveillance_score"]
    )


    # =====================================================
    # FINAL PRIORITY
    # =====================================================

    print("\n--- FINAL DECISION ---")

    print(
        "Final priority:",
        score_result["priority"]
    )


    # =====================================================
    # WHY?
    # =====================================================

    print("\n--- WHY THIS PRIORITY? ---")

    for reason in score_result["reasons"]:

        print("✓", reason)


    # =====================================================
    # ACTION
    # =====================================================

    print("\n--- RECOMMENDED ACTION ---")

    if score_result["priority"] == "URGENT":

        print(
            "• Isolate suspected animal/group"
        )

        print(
            "• Contact veterinary authorities"
        )

        print(
            "• Start veterinary investigation"
        )

        print(
            "• Collect samples for laboratory confirmation"
        )

    elif score_result["priority"] == "HIGH":

        print(
            "• Veterinary investigation recommended"
        )

        print(
            "• Increase surveillance of nearby animals"
        )

    elif score_result["priority"] == "MEDIUM":

        print(
            "• Increase monitoring"
        )

        print(
            "• Check nearby animals for symptoms"
        )

    else:

        print(
            "• Continue routine animal-health monitoring"
        )


    # =====================================================
    # FINAL RESULT
    # =====================================================

    print("\n==============================================")
    print("              FINAL AI RESULT")
    print("==============================================")

    print(
        "Animal:",
        case["Animal_Type"]
    )

    print(
        "Breed:",
        case["Breed"]
    )

    print(
        "District:",
        case["District"]
    )

    print(
        "Clinical ML prediction:",
        ml_result["prediction"]
    )

    print(
        "ML confidence:",
        f'{ml_result["confidence"]}%'
    )

    print(
        "FMD surveillance:",
        surveillance_result["fmd_risk"]
    )

    print(
        "FMD surveillance score:",
        surveillance_result["fmd_score"]
    )

    print(
        "Historical FMD risk:",
        surveillance_result["historical_risk"]
    )

    print(
        "District forecast:",
        surveillance_result["district_forecast"]
    )

    print(
        "Overall surveillance score:",
        score_result["surveillance_score"]
    )

    print(
        "FINAL PRIORITY:",
        score_result["priority"]
    )

    print("==============================================")