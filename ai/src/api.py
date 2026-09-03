import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# =========================================================
# MAKE ai/src AVAILABLE
# =========================================================

SRC_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# =========================================================
# IMPORT AI MODULES
# =========================================================

from ai_pipeline import (
    clinical_ml_prediction,
    calculate_surveillance_score
)

from case_assessment import assess_case

from schemas import AnimalCase


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(

    title="Animal Health Surveillance AI",

    description=(
        "AI-assisted livestock disease surveillance "
        "and risk prioritization system"
    ),

    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {

        "system":
            "Animal Health Surveillance AI",

        "status":
            "running",

        "version":
            "1.0.0"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "clinical_ml":
            "loaded",

        "fmd_surveillance":
            "active",

        "maharashtra_risk_engine":
            "active"
    }


# =========================================================
# ASSESS ANIMAL CASE
# =========================================================

@app.post("/assess")
def assess_animal(case: AnimalCase):

    # -----------------------------------------------------
    # Convert Pydantic model to dictionary
    # -----------------------------------------------------

    case_data = case.model_dump()


    # -----------------------------------------------------
    # CLINICAL ML
    # -----------------------------------------------------

    ml_result = clinical_ml_prediction(
        case_data
    )


    # -----------------------------------------------------
    # SURVEILLANCE
    # -----------------------------------------------------

    surveillance_result = assess_case(
        case_data
    )


    # -----------------------------------------------------
    # EXPLAINABLE SCORE
    # -----------------------------------------------------

    score_result = calculate_surveillance_score(

        ml_result,

        surveillance_result
    )


    # -----------------------------------------------------
    # RECOMMENDED ACTIONS
    # -----------------------------------------------------

    if score_result["priority"] == "URGENT":

        actions = [

            "Isolate suspected animal/group",

            "Contact veterinary authorities",

            "Start veterinary investigation",

            "Collect samples for laboratory confirmation"
        ]

    elif score_result["priority"] == "HIGH":

        actions = [

            "Veterinary investigation recommended",

            "Increase surveillance of nearby animals"
        ]

    elif score_result["priority"] == "MEDIUM":

        actions = [

            "Increase monitoring",

            "Check nearby animals for symptoms"
        ]

    else:

        actions = [

            "Continue routine animal-health monitoring"
        ]


    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "case": {

            "animal_type":
                case.Animal_Type,

            "breed":
                case.Breed,

            "age":
                case.Age,

            "gender":
                case.Gender,

            "district":
                case.District
        },


        "clinical_ml": {

            "prediction":
                ml_result["prediction"],

            "confidence":
                ml_result["confidence"],

            "top_predictions":
                ml_result["top_predictions"]
        },


        "fmd_surveillance": {

            "flag":
                surveillance_result["fmd_flag"],

            "score":
                surveillance_result["fmd_score"],

            "risk_level":
                surveillance_result["fmd_risk"],

            "reasons":
                surveillance_result["fmd_reasons"]
        },


        "maharashtra_surveillance": {

            "historical_fmd_risk":
                surveillance_result[
                    "historical_risk"
                ],

            "district_forecast":
                surveillance_result[
                    "district_forecast"
                ]
        },


        "final_assessment": {

            "surveillance_score":
                score_result[
                    "surveillance_score"
                ],

            "priority":
                score_result[
                    "priority"
                ],

            "reasons":
                score_result[
                    "reasons"
                ],

            "score_components":
                score_result[
                    "components"
                ]
        },


        "recommended_actions":
            actions
    }