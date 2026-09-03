import pandas as pd
from pathlib import Path


# -----------------------------
# File locations
# -----------------------------

INPUT_PATH = "ai/data/raw/cleaned_animal_disease_prediction.csv"
OUTPUT_PATH = "ai/data/processed/livestock_ml_dataset.csv"


# -----------------------------
# Load raw dataset
# -----------------------------

df = pd.read_csv(INPUT_PATH)

print("Original dataset:")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# -----------------------------
# Keep diseases with enough data
# -----------------------------

disease_counts = df["Disease_Prediction"].value_counts()

usable_diseases = disease_counts[disease_counts >= 10].index

df = df[df["Disease_Prediction"].isin(usable_diseases)].copy()


print("\nAfter filtering rare diseases:")
print("Rows:", len(df))
print("Diseases:", df["Disease_Prediction"].nunique())


# -----------------------------
# Convert Yes / No columns
# -----------------------------

yes_no_columns = [
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

for column in yes_no_columns:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"yes": 1, "no": 0})
    )


# -----------------------------
# Clean numerical columns
# -----------------------------

# -----------------------------
# Clean numerical columns
# -----------------------------

df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce")

# Body temperature contains °C text, so remove it first
df["Body_Temperature"] = (
    df["Body_Temperature"]
    .astype(str)
    .str.replace("°C", "", regex=False)
    .str.replace("Â", "", regex=False)
    .str.strip()
)

df["Body_Temperature"] = pd.to_numeric(
    df["Body_Temperature"],
    errors="coerce"
)

df["Heart_Rate"] = pd.to_numeric(
    df["Heart_Rate"],
    errors="coerce"
)

# -----------------------------
# Remove rows with missing data
# -----------------------------

df = df.dropna()


# -----------------------------
# Save processed dataset
# -----------------------------

Path("ai/data/processed").mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_PATH, index=False)


print("\n===== PREPROCESSING COMPLETE =====")
print("Final rows:", len(df))
print("Final columns:", len(df.columns))
print("Diseases:", df["Disease_Prediction"].nunique())

print("\nSaved to:")
print(OUTPUT_PATH)