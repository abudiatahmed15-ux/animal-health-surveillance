import pandas as pd

DATA_PATH = "ai/data/raw/maharashtra_surveillance.csv"

df = pd.read_csv(DATA_PATH)

print("\n===== MAHARASHTRA SURVEILLANCE DATA =====")

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\n===== COLUMNS =====")
print(df.columns.tolist())

print("\n===== DISEASES =====")
print(df["Disease"].value_counts(dropna=False))

print("\n===== YEARS =====")
print(df["Year"].value_counts().sort_index())

print("\n===== METRICS =====")
print(df["Metric"].value_counts())

print("\n===== ANIMAL TYPES =====")
print(df["Animal_Type"].value_counts(dropna=False))

print("\n===== DISTRICTS =====")
print(df["District"].value_counts(dropna=False))

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== FIRST 10 ROWS =====")
print(df.head(10).to_string(index=False))
