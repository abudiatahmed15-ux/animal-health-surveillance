import pandas as pd
import joblib

MODEL_PATH = "ai/models/livestock_disease_model.joblib"
DATA_PATH = "ai/data/raw/cleaned_animal_disease_prediction.csv"

print("Loading model and data...")

model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

# Clean temperature
df["Body_Temperature"] = (
    df["Body_Temperature"]
    .astype(str)
    .str.replace("°C", "", regex=False)
    .str.replace("Â", "", regex=False)
    .str.strip()
)

df["Body_Temperature"] = pd.to_numeric(
    df["Body_Temperature"], errors="coerce"
)

# Convert Yes/No fields
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

mapping = {
    "yes": 1,
    "no": 0,
    "true": 1,
    "false": 0
}

for col in binary_columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
    )

fmd = df[
    df["Disease_Prediction"].isin([
        "Foot-and-Mouth Disease",
        "Foot-and Mouth Disease"
    ])
].copy()

print("\nFMD records found:", len(fmd))

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

X = fmd[feature_columns]

predictions = model.predict(X)

try:
    probabilities = model.predict_proba(X)
    classes = model.classes_
except:
    probabilities = None

print("\n===== FMD MODEL TEST =====")

for i, prediction in enumerate(predictions):
    print("\nRecord", i + 1)
    print("Actual:     ", fmd.iloc[i]["Disease_Prediction"])
    print("Predicted:  ", prediction)

    if probabilities is not None:
        probs = probabilities[i]
        top_indices = probs.argsort()[-3:][::-1]

        print("Top predictions:")

        for idx in top_indices:
            print(
                f"  {classes[idx]} : {probs[idx] * 100:.2f}%"
            )

print("\n===== SUMMARY =====")
print("Actual FMD records:", len(fmd))
print(
    "Correctly predicted FMD:",
    sum(predictions == "Foot-and-Mouth Disease")
)