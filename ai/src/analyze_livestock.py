import pandas as pd

DATA_PATH = "ai/data/raw/cleaned_animal_disease_prediction.csv"

df = pd.read_csv(DATA_PATH)

# Keep livestock animals available in our dataset
livestock = df[df["Animal_Type"].isin(["Cow", "Horse"])]

print("\n===== LIVESTOCK DATA =====")
print("Total livestock records:", len(livestock))

print("\n===== LIVESTOCK ANIMAL TYPES =====")
print(livestock["Animal_Type"].value_counts())

print("\n===== LIVESTOCK DISEASES =====")

disease_counts = livestock["Disease_Prediction"].value_counts()

print(disease_counts)

print("\n===== DISEASES WITH AT LEAST 5 RECORDS =====")

useful_diseases = disease_counts[disease_counts >= 5]

print(useful_diseases)

print("\n===== NUMBER OF USABLE DISEASES =====")
print(len(useful_diseases))