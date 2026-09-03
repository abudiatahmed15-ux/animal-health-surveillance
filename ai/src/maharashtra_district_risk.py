import pandas as pd


HISTORICAL_PATH = (
    "ai/data/raw/processed/"
    "maharashtra_disease_risk.csv"
)

DISTRICT_PATH = (
    "ai/data/raw/processed/"
    "maharashtra_district_risk_forecast_2025.csv"
)

OUTPUT_PATH = (
    "ai/data/raw/processed/"
    "maharashtra_current_district_risk.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

historical = pd.read_csv(HISTORICAL_PATH)
district = pd.read_csv(DISTRICT_PATH)

print("\n===== MAHARASHTRA DISTRICT RISK =====")

print("Historical records:", len(historical))
print("District forecast records:", len(district))


# ============================================================
# DISEASE-LEVEL HISTORICAL SUMMARY
# ============================================================

historical_summary = (
    historical
    .groupby("Disease")
    .agg(
        Historical_Average_Risk=(
            "Risk_Score",
            "mean"
        ),

        Historical_Max_Risk=(
            "Risk_Score",
            "max"
        ),

        Historical_Records=(
            "Risk_Score",
            "count"
        )
    )
    .reset_index()
)


# ============================================================
# MERGE HISTORICAL RISK WITH DISTRICT FORECAST
# ============================================================

result = district.merge(
    historical_summary,
    on="Disease",
    how="left"
)


# ============================================================
# DISTRICT FORECAST SCORE
# ============================================================

result["District_Forecast_Score"] = (
    result["Forecast_Risk_Flag"] * 100
)


# ============================================================
# COMBINED RISK SCORE
# ============================================================

# Historical disease severity = 40%
# Current district forecast = 60%

result["Combined_Risk_Score"] = (
    0.40 * result["Historical_Average_Risk"]
    + 0.60 * result["District_Forecast_Score"]
)


# ============================================================
# FINAL RISK LEVEL
# ============================================================

def classify_risk(score):

    if score >= 75:
        return "VERY HIGH"

    elif score >= 50:
        return "HIGH"

    elif score >= 25:
        return "MODERATE"

    else:
        return "LOW"


result["Combined_Risk_Level"] = (
    result["Combined_Risk_Score"]
    .apply(classify_risk)
)


# ============================================================
# SURVEILLANCE PRIORITY
# ============================================================

def surveillance_priority(level):

    if level == "VERY HIGH":
        return "URGENT"

    elif level == "HIGH":
        return "HIGH"

    elif level == "MODERATE":
        return "MEDIUM"

    else:
        return "ROUTINE"


result["Surveillance_Priority"] = (
    result["Combined_Risk_Level"]
    .apply(surveillance_priority)
)


# ============================================================
# SORT
# ============================================================

result = result.sort_values(
    by="Combined_Risk_Score",
    ascending=False
)


# ============================================================
# SAVE
# ============================================================

result.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\n===== DISTRICT RISK RESULTS =====")

columns = [
    "District",
    "Disease",
    "Forecast_Month",
    "Historical_Average_Risk",
    "Historical_Max_Risk",
    "District_Forecast_Score",
    "Combined_Risk_Score",
    "Combined_Risk_Level",
    "Surveillance_Priority"
]

print(
    result[columns]
    .to_string(index=False)
)


print("\n===== RISK LEVEL COUNTS =====")

print(
    result["Combined_Risk_Level"]
    .value_counts()
)


print("\n===== DISTRICTS REQUIRING HIGH PRIORITY =====")

high_priority = result[
    result["Surveillance_Priority"].isin(
        ["URGENT", "HIGH"]
    )
]

print(
    high_priority[
        [
            "District",
            "Disease",
            "Combined_Risk_Score",
            "Combined_Risk_Level",
            "Surveillance_Priority"
        ]
    ].to_string(index=False)
)


print("\nSaved to:")
print(OUTPUT_PATH)