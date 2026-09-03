import pandas as pd

INPUT_PATH = "ai/data/raw/processed/maharashtra_disease_history_verified_v2.csv"
OUTPUT_PATH = "ai/data/raw/processed/maharashtra_disease_history_clean.csv"

# Load dataset
df = pd.read_csv(INPUT_PATH)

print("\n===== ORIGINAL DATA =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Clean text columns
text_columns = [
    "Period",
    "Disease",
    "Animal_Type",
    "Source",
    "Evidence"
]

for col in text_columns:
    df[col] = df[col].astype("string").str.strip()

# Convert numerical columns
numeric_columns = [
    "Year",
    "Outbreaks",
    "Cases",
    "Deaths"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Create mortality rate
df["Mortality_Rate"] = (
    df["Deaths"] / df["Cases"].replace(0, pd.NA)
)

# Replace infinite values
df["Mortality_Rate"] = df["Mortality_Rate"].replace(
    [float("inf"), float("-inf")],
    pd.NA
)

# Add disease names
disease_names = {
    "FMD": "Foot-and-Mouth Disease",
    "PPR": "Peste des Petits Ruminants",
    "HS": "Haemorrhagic Septicaemia",
    "BQ": "Black Quarter",
    "LSD": "Lumpy Skin Disease"
}

df["Disease_Name"] = df["Disease"].map(disease_names)

# Save cleaned dataset
df.to_csv(OUTPUT_PATH, index=False)

print("\n===== CLEANED DATA =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n===== DISEASES =====")
print(df["Disease"].value_counts())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== SAMPLE =====")
print(df.head(10).to_string(index=False))

print("\nSaved to:")
print(OUTPUT_PATH)