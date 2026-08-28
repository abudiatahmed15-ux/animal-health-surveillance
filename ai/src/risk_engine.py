# Animal Health Risk Engine
# SIH 2026 - Problem Statement 26128


DISEASE_WEIGHTS = {

    "Foot-and-Mouth Disease": {
        "fever": 10,
        "mouth_lesions": 30,
        "excessive_salivation": 25,
        "lameness": 20,
    },

    "Hemorrhagic Septicemia": {
        "fever": 30,
        "swelling": 25,
        "breathing_difficulty": 25,
        "nasal_discharge": 15,
    },

    "Brucellosis": {
        "abortion": 35,
        "infertility": 25,
        "retained_placenta": 20,
        "fever": 10,
    },

    "Mastitis": {
        "udder_swelling": 30,
        "abnormal_milk": 30,
        "udder_pain": 25,
        "fever": 10,
    },

    "Peste des Petits Ruminants": {
        "fever": 20,
        "nasal_discharge": 20,
        "diarrhea": 25,
        "mouth_lesions": 20,
        "loss_of_appetite": 10,
    }
}


def calculate_disease_scores(symptoms):
    """Calculate scores for each possible disease."""

    scores = {}

    for disease, weights in DISEASE_WEIGHTS.items():

        score = 0

        for symptom in symptoms:

            if symptom in weights:
                score += weights[symptom]

        scores[disease] = score

    return scores


def calculate_outbreak_risk(case):
    """Calculate overall outbreak risk."""

    risk_score = 0

    affected = case["affected_count"]
    deaths = case["deaths"]
    vaccination = case["vaccination_status"]
    duration = case["symptom_duration_days"]
    nearby = case["nearby_cases"]

    # Number of affected animals
    if affected >= 20:
        risk_score += 30

    elif affected >= 10:
        risk_score += 20

    elif affected >= 5:
        risk_score += 10

    # Deaths
    if deaths >= 5:
        risk_score += 30

    elif deaths >= 2:
        risk_score += 20

    elif deaths >= 1:
        risk_score += 10

    # Vaccination status
    if vaccination == "none":
        risk_score += 20

    elif vaccination == "partial":
        risk_score += 10

    elif vaccination == "unknown":
        risk_score += 5

    # Duration of symptoms
    if duration >= 7:
        risk_score += 10

    elif duration >= 3:
        risk_score += 5

    # Nearby cases
    if nearby >= 10:
        risk_score += 20

    elif nearby >= 5:
        risk_score += 10

    elif nearby >= 1:
        risk_score += 5

    return risk_score


def get_risk_level(score):
    """Convert risk score into a risk level."""

    if score >= 70:
        return "CRITICAL"

    elif score >= 50:
        return "HIGH"

    elif score >= 25:
        return "MEDIUM"

    else:
        return "LOW"


def get_recommendation(risk_level):
    """Provide an action based on risk level."""

    recommendations = {

        "LOW":
            "Continue monitoring the animal.",

        "MEDIUM":
            "Monitor closely and contact a veterinary worker if symptoms worsen.",

        "HIGH":
            "Arrange veterinary inspection and consider isolating affected animals.",

        "CRITICAL":
            "Immediate veterinary inspection. Isolate affected animals and report the suspected outbreak."
    }

    return recommendations[risk_level]


def predict_case(case):

    symptoms = case["symptoms"]

    # Disease prediction
    disease_scores = calculate_disease_scores(symptoms)

    predicted_disease = max(
        disease_scores,
        key=disease_scores.get
    )

    disease_score = disease_scores[predicted_disease]

    # Outbreak risk
    outbreak_score = calculate_outbreak_risk(case)

    risk_level = get_risk_level(outbreak_score)

    recommendation = get_recommendation(risk_level)

    return {

        "animal_type": case["animal_type"],

        "possible_disease": predicted_disease,

        "disease_score": disease_score,

        "outbreak_score": outbreak_score,

        "risk_level": risk_level,

        "recommendation": recommendation,

        "all_disease_scores": disease_scores
    }


# Test the system
if __name__ == "__main__":

    case = {

        "animal_type": "cow",

        "age": 4,

        "symptoms": [
            "fever",
             "swelling",
            "breathing_difficulty",
            "nasal_discharge"
        ],

        "affected_count": 7,

        "deaths": 1,

        "vaccination_status": "partial",

        "symptom_duration_days": 3,

        "nearby_cases": 4
    }

    result = predict_case(case)

    print("\nANIMAL HEALTH RISK ASSESSMENT")
    print("--------------------------------")

    print("Animal Type:", result["animal_type"])

    print("Possible Disease:",
          result["possible_disease"])

    print("Disease Score:",
          result["disease_score"])

    print("Outbreak Score:",
          result["outbreak_score"])

    print("Risk Level:",
          result["risk_level"])

    print("Recommendation:",
          result["recommendation"])

    print("\nDisease Scores:")

    for disease, score in result["all_disease_scores"].items():

        print(f"{disease}: {score}")