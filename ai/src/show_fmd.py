import pandas as pd

DATA_PATH = "ai/data/raw/cleaned_animal_disease_prediction.csv"

df = pd.read_csv(DATA_PATH)

fmd = df[
    df["Disease_Prediction"].isin([
        "Foot-and-Mouth Disease",
        "Foot-and Mouth Disease"
    ])
]

columns = [
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
    "Heart_Rate",
    "Disease_Prediction"
]

print("\n===== FMD RECORDS =====\n")

print(fmd[columns].to_string(index=False))

print("\n===== FMD SYMPTOM FREQUENCY =====")

for col in [
    "Symptom_1",
    "Symptom_2",
    "Symptom_3",
    "Symptom_4"
]:
    print(f"\n{col}:")
    print(fmd[col].value_counts().to_string())