# Animal Health Disease Risk Engine
# Prototype for SIH 2026 Problem Statement 26128


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
    """
    Calculate a score for each disease based on reported symptoms.
    """

    scores = {}

    for disease, weights in DISEASE_WEIGHTS.items():

        score = 0

        for symptom in symptoms:

            if symptom in weights:
                score += weights[symptom]

        scores[disease] = score

    return scores


def get_risk_level(score):
    """
    Convert a numerical score into a risk category.
    """

    if score >= 70:
        return "CRITICAL"

    elif score >= 50:
        return "HIGH"

    elif score >= 25:
        return "MEDIUM"

    else:
        return "LOW"


def predict_disease(symptoms):
    """
    Predict the most likely disease based on symptoms.
    """

    scores = calculate_disease_scores(symptoms)

    predicted_disease = max(scores, key=scores.get)

    predicted_score = scores[predicted_disease]

    risk_level = get_risk_level(predicted_score)

    return {
        "possible_disease": predicted_disease,
        "score": predicted_score,
        "risk_level": risk_level,
        "all_scores": scores
    }


if __name__ == "__main__":

    # Example animal report
    symptoms = [
    "fever",
    "nasal_discharge",
    "breathing_difficulty",
    "swelling"
]


    result = predict_disease(symptoms)

    print("\nANIMAL HEALTH RISK ASSESSMENT")
    print("--------------------------------")

    print("Possible Disease:", result["possible_disease"])
    print("Risk Score:", result["score"])
    print("Risk Level:", result["risk_level"])

    print("\nDisease Scores:")

    for disease, score in result["all_scores"].items():
        print(f"{disease}: {score}")