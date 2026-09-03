import re


def normalize(value):
    """Convert a value into a simple lowercase string."""
    if value is None:
        return ""

    if isinstance(value, float):
        if value != value:  # NaN
            return ""

    return str(value).strip().lower()


def contains_any(text, keywords):
    """Check whether any keyword appears in text."""
    text = normalize(text)

    return any(keyword in text for keyword in keywords)


def fmd_surveillance_check(case):
    """
    FMD surveillance screening.

    IMPORTANT:
    This is NOT a diagnosis.
    It identifies cases that deserve veterinary investigation
    and possible laboratory confirmation.
    """

    score = 0
    reasons = []

    animal_type = normalize(case.get("Animal_Type"))

    symptoms = [
        case.get("Symptom_1"),
        case.get("Symptom_2"),
        case.get("Symptom_3"),
        case.get("Symptom_4"),
    ]

    symptoms_text = " ".join(
        normalize(symptom)
        for symptom in symptoms
        if normalize(symptom)
    )

    # ---------------------------------------------------------
    # 1. SUSCEPTIBLE ANIMAL
    # ---------------------------------------------------------

    susceptible = [
        "cow",
        "cattle",
        "buffalo",
        "sheep",
        "goat",
        "pig",
        "swine"
    ]

    if any(animal in animal_type for animal in susceptible):
        score += 10

    # ---------------------------------------------------------
    # 2. MOUTH / FOOT LESIONS
    # ---------------------------------------------------------

    lesion_keywords = [
        "mouth lesion",
        "mouth lesions",
        "oral lesion",
        "oral lesions",
        "mouth blister",
        "mouth blisters",
        "vesicle",
        "vesicles",
        "blister",
        "blisters",
        "foot lesion",
        "foot lesions",
        "hoof lesion",
        "hoof lesions",
        "hoof blister",
        "hoof blisters",
        "interdigital lesion"
    ]

    if contains_any(symptoms_text, lesion_keywords):
        score += 40
        reasons.append("mouth/foot lesion or vesicle reported")

    # ---------------------------------------------------------
    # 3. LAMENESS
    # ---------------------------------------------------------

    if contains_any(
        symptoms_text,
        ["lameness", "lame", "difficulty walking", "reluctance to move"]
    ):
        score += 20
        reasons.append("lameness or movement difficulty reported")

    # ---------------------------------------------------------
    # 4. SALIVATION / DROOLING
    # ---------------------------------------------------------

    if contains_any(
        symptoms_text,
        ["salivation", "drooling", "excessive saliva", "hypersalivation"]
    ):
        score += 15
        reasons.append("excessive salivation reported")

    # ---------------------------------------------------------
    # 5. FEVER
    # ---------------------------------------------------------

    if contains_any(
        symptoms_text,
        ["fever", "high fever", "pyrexia"]
    ):
        score += 10
        reasons.append("fever reported")

    # ---------------------------------------------------------
    # 6. APPETITE LOSS
    # ---------------------------------------------------------

    appetite = normalize(case.get("Appetite_Loss"))

    if appetite in ["yes", "true", "1"]:
        score += 5
        reasons.append("loss of appetite reported")

    # ---------------------------------------------------------
    # 7. WEIGHT LOSS
    # ---------------------------------------------------------

    if contains_any(
        symptoms_text,
        ["weight loss", "loss of weight"]
    ):
        score += 5
        reasons.append("weight loss reported")

    # ---------------------------------------------------------
    # 8. SKIN LESIONS
    # ---------------------------------------------------------

    skin_lesions = normalize(case.get("Skin_Lesions"))

    if skin_lesions in ["yes", "true", "1"]:
        score += 5
        reasons.append("skin lesions reported")

    # ---------------------------------------------------------
    # FINAL RISK
    # ---------------------------------------------------------

    # Cap score at 100
    score = min(score, 100)

    if score >= 60:
        risk_level = "HIGH"
    elif score >= 35:
        risk_level = "MODERATE"
    elif score >= 15:
        risk_level = "LOW"
    else:
        risk_level = "VERY LOW"

    # Strong FMD-specific signs
    strong_sign = (
        contains_any(symptoms_text, lesion_keywords)
        or contains_any(
            symptoms_text,
            ["salivation", "drooling", "hypersalivation"]
        )
    )

    if score >= 60 or (strong_sign and score >= 35):
        flag = True
    else:
        flag = False

    if not reasons:
        reasons.append("no strong FMD-specific clinical sign identified")

    return {
        "FMD_Flag": flag,
        "FMD_Score": score,
        "FMD_Risk_Level": risk_level,
        "FMD_Reasons": reasons
    }


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    test_case = {
        "Animal_Type": "Cow",
        "Symptom_1": "Fever",
        "Symptom_2": "Mouth lesions",
        "Symptom_3": "Lameness",
        "Symptom_4": "Excessive salivation",
        "Appetite_Loss": "Yes",
        "Skin_Lesions": "No"
    }

    result = fmd_surveillance_check(test_case)

    print("\n===== FMD SURVEILLANCE TEST =====")

    for key, value in result.items():
        print(f"{key}: {value}")