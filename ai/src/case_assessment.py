import pandas as pd
from fmd_surveillance import fmd_surveillance_check


HISTORY_PATH = "ai/data/raw/processed/maharashtra_disease_risk.csv"
FORECAST_PATH = "ai/data/raw/processed/maharashtra_district_risk_forecast_2025.csv"


def assess_case(case):

    # -----------------------------------------------------
    # LOAD SURVEILLANCE DATA
    # -----------------------------------------------------

    history = pd.read_csv(HISTORY_PATH)
    forecast = pd.read_csv(FORECAST_PATH)

    # -----------------------------------------------------
    # FMD SCREENING
    # -----------------------------------------------------

    fmd_result = fmd_surveillance_check(case)

    # -----------------------------------------------------
    # HISTORICAL FMD RISK
    # -----------------------------------------------------

    fmd_history = history[
        history["Disease"].astype(str).str.upper() == "FMD"
    ]

    if len(fmd_history) > 0:
        historical_risk = fmd_history["Risk_Score"].mean()
    else:
        historical_risk = 0

    # -----------------------------------------------------
    # DISTRICT FORECAST
    # -----------------------------------------------------

    district = str(case.get("District", "")).strip()

    district_forecast = forecast[
        (
            forecast["Disease"]
            .astype(str)
            .str.upper()
            == "FMD"
        )
        &
        (
            forecast["District"]
            .astype(str)
            .str.lower()
            == district.lower()
        )
    ]

    forecast_available = len(district_forecast) > 0

    # -----------------------------------------------------
    # FINAL PRIORITY
    # -----------------------------------------------------

    if fmd_result["FMD_Flag"] and forecast_available:
        priority = "URGENT"

    elif fmd_result["FMD_Flag"]:
        priority = "HIGH"

    elif forecast_available:
        priority = "MEDIUM"

    else:
        priority = "ROUTINE"

    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    if priority == "URGENT":

        action = [
            "Isolate suspected animal/group",
            "Contact veterinary authorities",
            "Start veterinary investigation",
            "Collect samples for laboratory confirmation"
        ]

    elif priority == "HIGH":

        action = [
            "Veterinary investigation recommended",
            "Increase surveillance of nearby animals"
        ]

    elif priority == "MEDIUM":

        action = [
            "Increase monitoring",
            "Check nearby animals for symptoms"
        ]

    else:

        action = [
            "Continue routine animal-health monitoring"
        ]

    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {
        "disease_screened": "FMD",
        "animal_type": case.get("Animal_Type"),
        "district": district,
        "fmd_flag": fmd_result["FMD_Flag"],
        "fmd_score": fmd_result["FMD_Score"],
        "fmd_risk": fmd_result["FMD_Risk_Level"],
        "fmd_reasons": fmd_result["FMD_Reasons"],
        "historical_risk": round(historical_risk, 2),
        "district_forecast": (
            "HIGH_OR_VERY_HIGH"
            if forecast_available
            else "NONE"
        ),
        "final_priority": priority,
        "recommended_actions": action
    }


# =========================================================
# DEMO
# =========================================================

if __name__ == "__main__":

    case = {

        "Animal_Type": "Cow",

        "District": "Ahmadnagar",

        "Age": 4,

        "Temperature": 40.2,

        "Symptom_1": "Fever",

        "Symptom_2": "Mouth lesions",

        "Symptom_3": "Lameness",

        "Symptom_4": "Excessive salivation",

        "Appetite_Loss": "Yes",

        "Skin_Lesions": "No"
    }

    result = assess_case(case)

    print("\n========================================")
    print("       ANIMAL HEALTH CASE ASSESSMENT")
    print("========================================")

    print("\nAnimal Type:", result["animal_type"])
    print("District:", result["district"])

    print("\n--- FMD SCREENING ---")

    print("FMD Flag:", result["fmd_flag"])
    print("FMD Score:", result["fmd_score"])
    print("FMD Risk:", result["fmd_risk"])

    print("\nReasons:")

    for reason in result["fmd_reasons"]:
        print("-", reason)

    print("\n--- MAHARASHTRA SURVEILLANCE ---")

    print(
        "Historical FMD Risk:",
        result["historical_risk"]
    )

    print(
        "District Forecast:",
        result["district_forecast"]
    )

    print("\n--- FINAL DECISION ---")

    print(
        "Priority:",
        result["final_priority"]
    )

    print("\nRecommended Actions:")

    for action in result["recommended_actions"]:
        print("-", action)

    print("\n========================================")