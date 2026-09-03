import pandas as pd

INPUT_PATH = "ai/data/raw/processed/maharashtra_disease_history_clean.csv"
OUTPUT_PATH = "ai/data/raw/processed/maharashtra_disease_risk.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_PATH)

print("\n===== MAHARASHTRA RISK ENGINE v2 =====")
print("Input rows:", len(df))


# ============================================================
# CLEAN NUMERIC DATA
# ============================================================

numeric_columns = [
    "Year",
    "Outbreaks",
    "Cases",
    "Deaths"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# ============================================================
# PREPARE SCORING VALUES
# ============================================================

df["Outbreaks_Score_Base"] = df["Outbreaks"].fillna(0)
df["Cases_Score_Base"] = df["Cases"].fillna(0)
df["Deaths_Score_Base"] = df["Deaths"].fillna(0)


# ============================================================
# DISEASE-SPECIFIC NORMALIZATION
# ============================================================

def normalize_by_group(series):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(
            0.0,
            index=series.index
        )

    return (
        series - minimum
    ) / (
        maximum - minimum
    )


df["Outbreak_Score"] = (
    df.groupby("Disease")["Outbreaks_Score_Base"]
    .transform(normalize_by_group)
)

df["Case_Score"] = (
    df.groupby("Disease")["Cases_Score_Base"]
    .transform(normalize_by_group)
)

df["Death_Score"] = (
    df.groupby("Disease")["Deaths_Score_Base"]
    .transform(normalize_by_group)
)


# ============================================================
# RECENCY SCORE
# ============================================================

latest_year = df["Year"].max()

df["Years_Ago"] = latest_year - df["Year"]

df["Recency_Score"] = (
    1 / (1 + df["Years_Ago"])
)


# ============================================================
# TREND SCORE
# ============================================================

# Calculate the earliest and latest case values
# for each disease.

first_cases = (
    df.sort_values("Year")
    .groupby("Disease")["Cases_Score_Base"]
    .first()
)

last_cases = (
    df.sort_values("Year")
    .groupby("Disease")["Cases_Score_Base"]
    .last()
)


trend_values = {}

for disease in first_cases.index:

    first_value = first_cases.loc[disease]
    last_value = last_cases.loc[disease]

    if first_value == 0:
        trend = 0
    else:
        trend = (
            last_value - first_value
        ) / first_value

    # Limit trend between -1 and +1
    trend = max(min(trend, 1), -1)

    trend_values[disease] = trend


df["Trend_Score"] = df["Disease"].map(
    trend_values
)


# Convert -1 to +1 into 0 to 1
df["Trend_Normalized"] = (
    (df["Trend_Score"] + 1) / 2
)


# ============================================================
# FINAL RISK SCORE
# ============================================================

df["Risk_Score"] = (
    0.30 * df["Outbreak_Score"]
    + 0.25 * df["Case_Score"]
    + 0.20 * df["Death_Score"]
    + 0.15 * df["Recency_Score"]
    + 0.10 * df["Trend_Normalized"]
) * 100


# ============================================================
# RISK CATEGORY
# ============================================================

def risk_category(score):

    if score >= 75:
        return "VERY HIGH"

    elif score >= 50:
        return "HIGH"

    elif score >= 25:
        return "MODERATE"

    else:
        return "LOW"


df["Risk_Level"] = df["Risk_Score"].apply(
    risk_category
)


# ============================================================
# SORT RESULTS
# ============================================================

df = df.sort_values(
    by="Risk_Score",
    ascending=False
)


# ============================================================
# SAVE RESULT
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n===== RISK LEVEL COUNTS =====")

print(
    df["Risk_Level"].value_counts()
)


print("\n===== TOP 20 RISK RECORDS =====")

columns_to_show = [
    "Year",
    "Period",
    "Disease",
    "Animal_Type",
    "Outbreaks",
    "Cases",
    "Deaths",
    "Risk_Score",
    "Risk_Level"
]

print(
    df[columns_to_show]
    .head(20)
    .to_string(index=False)
)


print("\n===== DISEASE SUMMARY =====")

summary = (
    df.groupby("Disease")
    .agg(
        Records=("Disease", "size"),
        Average_Risk=("Risk_Score", "mean"),
        Maximum_Risk=("Risk_Score", "max")
    )
    .sort_values(
        "Average_Risk",
        ascending=False
    )
)

print(
    summary.to_string()
)


print("\nSaved to:")
print(OUTPUT_PATH)