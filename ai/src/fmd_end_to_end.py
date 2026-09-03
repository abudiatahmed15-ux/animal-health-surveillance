import pandas as pd

from fmd_surveillance import fmd_surveillance_check


# =========================================================
# FILE PATHS
# =========================================================

HISTORY_PATH = "ai/data/raw/processed/maharashtra_disease_risk.csv"

FORECAST_PATH = (
    "ai/data/raw/processed/"
    "maharashtra_district_risk_forecast_2025.csv"
)


# =========================================================
# LOAD MAHARASHTRA DATA
# =========================================================

print("\nLoading Maharashtra surveillance data...")

history = pd.read_csv(HISTORY_PATH)
forecast = pd.read_csv(FORECAST_PATH)

print("Historical records:", len(history))
print("Forecast records:", len(forecast))


# =========================================================
# SIMULATED FIELD CASE
# =========================================================
# IMPORTANT:
# This is a DEMONSTRATION CASE.
# It is NOT a real animal diagnosis.
#
# The additional FMD-specific fields represent information
# that our future farmer/field-worker form should collect.
# =========================================================

case = {
    "Animal_Type": "Cow",
    "Age": 4,
    "Temperature": 40.2,

    "Symptom_1": "Fever",
    "Symptom_2": "Mouth lesions",
    "Symptom_3": "Lameness",
    "Symptom_4": "Excessive salivation",

    "Appetite_Loss": "Yes",
    "Skin_Lesions": "No"
}


# =========================================================
# FMD SURVEILLANCE
# =========================================================

print("\n===== FMD SURVEILLANCE =====")

fmd_result = fmd_surveillance_check(case)

print("FMD Flag:", fmd_result["FMD_Flag"])
print("FMD Score:", fmd_result["FMD_Score"])
print("FMD Risk:", fmd_result["FMD_Risk_Level"])

print("\nReasons:")

for reason in fmd_result["FMD_Reasons"]:
    print("-", reason)


# =========================================================
# HISTORICAL FMD RISK
# =========================================================

print("\n===== HISTORICAL FMD RISK =====")

fmd_history = history[
    history["Disease"].astype(str).str.upper() == "FMD"
]

if len(fmd_history) > 0:

    historical_risk = fmd_history["Risk_Score"].mean()

    print(
        f"Average historical FMD risk: "
        f"{historical_risk:.2f}"
    )

else:

    historical_risk = 0

    print("No historical FMD risk data found.")


# =========================================================
# DISTRICT FORECAST
# =========================================================

print("\n===== DISTRICT FORECAST =====")

fmd_forecast = forecast[
    forecast["Disease"].astype(str).str.upper() == "FMD"
]

if len(fmd_forecast) > 0:

    # Use first available forecast district
    district = fmd_forecast.iloc[0]["District"]

    district_match = fmd_forecast[
        fmd_forecast["District"] == district
    ]

    print("Selected district:", district)
    print("Forecast:", "HIGH_OR_VERY_HIGH")
    print("Forecast source: ICAR-NIVEDI NADRES")

else:

    district = "Unknown"

    print("No FMD district forecast available.")


# =========================================================
# FINAL PRIORITY
# =========================================================

print("\n===== FINAL SURVEILLANCE PRIORITY =====")

if (
    fmd_result["FMD_Flag"]
    and len(fmd_forecast) > 0
):

    priority = "URGENT"

elif fmd_result["FMD_Flag"]:

    priority = "HIGH"

elif len(fmd_forecast) > 0:

    priority = "MEDIUM"

else:

    priority = "ROUTINE"


print("Priority:", priority)


# =========================================================
# RECOMMENDED ACTION
# =========================================================

print("\n===== RECOMMENDED ACTION =====")

if priority == "URGENT":

    print(
        "• Isolate the suspected animal/group."
    )

    print(
        "• Contact veterinary authorities."
    )

    print(
        "• Initiate veterinary investigation."
    )

    print(
        "• Collect and refer samples for "
        "laboratory confirmation."
    )

elif priority == "HIGH":

    print(
        "• Veterinary investigation recommended."
    )

    print(
        "• Increase surveillance of nearby animals."
    )

elif priority == "MEDIUM":

    print(
        "• Continue enhanced monitoring."
    )

else:

    print(
        "• Continue routine animal-health monitoring."
    )


# =========================================================
# FINAL SUMMARY
# =========================================================

print("\n==========================================")
print("        ANIMAL HEALTH SURVEILLANCE")
print("==========================================")

print("Disease screened       : FMD")
print("Animal type            :", case["Animal_Type"])
print("District               :", district)
print(
    "FMD surveillance risk  :",
    fmd_result["FMD_Risk_Level"]
)
print(
    "Historical risk        :",
    f"{historical_risk:.2f}"
)
print(
    "District forecast      :",
    "HIGH_OR_VERY_HIGH"
    if len(fmd_forecast) > 0
    else "NONE"
)
print("Final priority         :", priority)

print("==========================================")