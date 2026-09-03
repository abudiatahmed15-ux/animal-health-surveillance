import joblib
import pandas as pd


# ============================================================
# FILE PATHS
# ============================================================

MODEL_PATH = "ai/models/livestock_disease_model.joblib"

CLINICAL_DATA_PATH = (
    "ai/data/raw/cleaned_animal_disease_prediction.csv"
)

HISTORICAL_PATH = (
    "ai/data/raw/processed/"
    "maharashtra_disease_risk.csv"
)

DISTRICT_PATH = (
    "ai/data/raw/processed/"
    "maharashtra_district_risk_forecast_2025.csv"
)


# ============================================================
# LOAD MODEL AND DATA
# ============================================================

print("\nLoading system...")

model = joblib.load(MODEL_PATH)

clinical_data = pd.read_csv(
    CLINICAL_DATA_PATH
)

historical = pd.read_csv(
    HISTORICAL_PATH
)

district_risk = pd.read_csv(
    DISTRICT_PATH
)


# ============================================================
# CLEAN CLINICAL DATA
# ============================================================

# Clean body temperature

clinical_data["Body_Temperature"] = (
    clinical_data["Body_Temperature"]
    .astype(str)
    .str.replace("°C", "", regex=False)
    .str.replace("Â", "", regex=False)
    .str.strip()
)

clinical_data["Body_Temperature"] = pd.to_numeric(
    clinical_data["Body_Temperature"],
    errors="coerce"
)


# Convert Yes / No values

binary_columns = [
    "Appetite_Loss",
    "Vomiting",
    "Diarrhea",
    "Coughing",
    "Labored_Breathing",
    "Lameness",
    "Skin_Lesions",
    "Nasal_Discharge",
    "Eye_Discharge"
]


for column in binary_columns:

    clinical_data[column] = (
        clinical_data[column]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace(
            {
                "yes": 1,
                "no": 0,
                "true": 1,
                "false": 0
            }
        )
    )

    clinical_data[column] = pd.to_numeric(
        clinical_data[column],
        errors="coerce"
    )


# ============================================================
# MODEL INPUT COLUMNS
# ============================================================

model_columns = [
    "Animal_Type",
    "Breed",
    "Gender",
    "Symptom_1",
    "Symptom_2",
    "Symptom_3",
    "Symptom_4",
    "Duration",
    "Age",
    "Weight",
    "Body_Temperature",
    "Heart_Rate",
    "Appetite_Loss",
    "Vomiting",
    "Diarrhea",
    "Coughing",
    "Labored_Breathing",
    "Lameness",
    "Skin_Lesions",
    "Nasal_Discharge",
    "Eye_Discharge"
]


# ============================================================
# FIND AN ACTUAL FMD RECORD
# ============================================================

fmd_records = clinical_data[
    clinical_data["Disease_Prediction"]
    .astype(str)
    .str.strip()
    .isin([
        "Foot-and-Mouth Disease",
        "Foot-and Mouth Disease"
    ])
]


print(
    "\nFMD records available:",
    len(fmd_records)
)


# ============================================================
# TEST FMD RECORDS UNTIL MODEL PREDICTS FMD
# ============================================================

selected_record = None
predicted_disease = None
confidence = None


for _, row in fmd_records.iterrows():

    sample = row[
        model_columns
    ].to_dict()

    input_df = pd.DataFrame(
        [sample]
    )

    try:

        prediction = model.predict(
            input_df
        )[0]

        probabilities = model.predict_proba(
            input_df
        )[0]

        confidence_value = probabilities.max()

    except Exception as error:

        continue


    if prediction == "Foot-and-Mouth Disease":

        selected_record = sample

        predicted_disease = prediction

        confidence = confidence_value

        break


# ============================================================
# CHECK RESULT
# ============================================================

if selected_record is None:

    print(
        "\nThe model did not predict FMD for "
        "any available FMD test record."
    )

    print(
        "This is not an error. It means the current "
        "clinical model needs further validation."
    )

    raise SystemExit


# ============================================================
# SELECT A DISTRICT WITH FMD FORECAST
# ============================================================

fmd_districts = district_risk[
    district_risk["Disease"]
    == "FMD"
]


if len(fmd_districts) > 0:

    selected_district = (
        fmd_districts.iloc[0]["District"]
    )

else:

    selected_district = "Pune"


# ============================================================
# HISTORICAL FMD RISK
# ============================================================

historical_fmd = historical[
    historical["Disease"]
    == "FMD"
]


if len(historical_fmd) > 0:

    historical_average = (
        historical_fmd["Risk_Score"]
        .mean()
    )

    historical_maximum = (
        historical_fmd["Risk_Score"]
        .max()
    )

else:

    historical_average = 0

    historical_maximum = 0


# ============================================================
# DISTRICT FORECAST
# ============================================================

district_match = district_risk[
    (district_risk["District"] == selected_district)
    &
    (district_risk["Disease"] == "FMD")
]


if len(district_match) > 0:

    forecast_flag = 1

    forecast_level = (
        district_match.iloc[0]
        ["Forecast_Risk_Level"]
    )

else:

    forecast_flag = 0

    forecast_level = (
        "NO CURRENT FORECAST MATCH"
    )


# ============================================================
# FINAL SURVEILLANCE PRIORITY
# ============================================================

if (
    forecast_flag == 1
    and confidence >= 0.70
):

    priority = "URGENT"


elif forecast_flag == 1:

    priority = "HIGH"


elif confidence >= 0.70:

    priority = "MEDIUM"


else:

    priority = "ROUTINE"


# ============================================================
# RECOMMENDED ACTION
# ============================================================

if priority == "URGENT":

    action = (
        "Immediate veterinary assessment and "
        "field investigation recommended."
    )


elif priority == "HIGH":

    action = (
        "Prioritize veterinary follow-up and "
        "enhanced surveillance."
    )


elif priority == "MEDIUM":

    action = (
        "Veterinary verification recommended."
    )


else:

    action = (
        "Continue monitoring and arrange "
        "veterinary verification if symptoms worsen."
    )


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n")
print("=" * 70)

print(
    "          LIVESTOCK AI EARLY WARNING SYSTEM"
)

print("=" * 70)


print("\n--- FARMER / FIELD REPORT ---")

print(
    "Animal Type :",
    selected_record["Animal_Type"]
)

print(
    "Breed       :",
    selected_record["Breed"]
)

print(
    "Gender      :",
    selected_record["Gender"]
)

print(
    "Symptoms    :",
    selected_record["Symptom_1"],
    "|",
    selected_record["Symptom_2"],
    "|",
    selected_record["Symptom_3"],
    "|",
    selected_record["Symptom_4"]
)


print("\n--- CLINICAL AI ---")

print(
    "Predicted Disease :",
    predicted_disease
)

print(
    "AI Confidence     :",
    round(
        confidence * 100,
        2
    ),
    "%"
)


print("\n--- MAHARASHTRA HISTORICAL RISK ---")

print(
    "Average FMD Risk :",
    round(
        historical_average,
        2
    )
)

print(
    "Maximum FMD Risk :",
    round(
        historical_maximum,
        2
    )
)


print("\n--- DISTRICT FORECAST ---")

print(
    "District :",
    selected_district
)

print(
    "Forecast :",
    forecast_level
)


print("\n--- FINAL SURVEILLANCE DECISION ---")

print(
    "Priority :",
    priority
)


print("\n--- RECOMMENDED ACTION ---")

print(
    action
)


print("\n")
print("=" * 70)

print(
    "                END OF ASSESSMENT"
)

print("=" * 70)