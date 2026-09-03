import os
import shutil
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# PATHS
# ============================================================

DATA_PATH = (
    "ai/data/raw/cleaned_animal_disease_prediction.csv"
)

MODEL_PATH = (
    "ai/models/livestock_disease_model.joblib"
)

BACKUP_MODEL_PATH = (
    "ai/models/livestock_disease_model_backup.joblib"
)


# ============================================================
# SETTINGS
# ============================================================

MIN_RECORDS_PER_DISEASE = 10

RANDOM_STATE = 42


# ============================================================
# LOAD DATA
# ============================================================

print("\n==============================================")
print("       LIVESTOCK DISEASE MODEL TRAINING")
print("==============================================")

df = pd.read_csv(DATA_PATH)

print("\nOriginal rows:", len(df))


# ============================================================
# NORMALIZE DISEASE NAMES
# ============================================================

print("\nNormalizing disease names...")

df["Disease_Prediction"] = (
    df["Disease_Prediction"]
    .astype(str)
    .str.strip()
)

# Merge duplicate FMD spelling

df["Disease_Prediction"] = (
    df["Disease_Prediction"]
    .replace(
        {
            "Foot-and Mouth Disease":
                "Foot-and-Mouth Disease"
        }
    )
)


# ============================================================
# SHOW DISEASE COUNTS
# ============================================================

disease_counts = (
    df["Disease_Prediction"]
    .value_counts()
)

print("\n===== DISEASE COUNTS =====")

print(
    disease_counts.to_string()
)


# ============================================================
# SELECT DISEASES
# ============================================================

valid_diseases = (
    disease_counts[
        disease_counts >= MIN_RECORDS_PER_DISEASE
    ]
    .index
    .tolist()
)


print(
    "\nMinimum records per disease:",
    MIN_RECORDS_PER_DISEASE
)

print("\nDiseases selected for training:")

for disease in valid_diseases:

    print(
        "-",
        disease,
        ":",
        disease_counts[disease],
        "records"
    )


# ============================================================
# FILTER DATA
# ============================================================

df = df[
    df["Disease_Prediction"].isin(
        valid_diseases
    )
].copy()


print(
    "\nTraining rows:",
    len(df)
)

print(
    "Number of disease classes:",
    df["Disease_Prediction"].nunique()
)


# ============================================================
# FEATURES
# ============================================================

TARGET = "Disease_Prediction"

FEATURES = [
    "Animal_Type",
    "Breed",
    "Age",
    "Gender",
    "Weight",
    "Symptom_1",
    "Symptom_2",
    "Symptom_3",
    "Symptom_4",
    "Duration",
    "Appetite_Loss",
    "Vomiting",
    "Diarrhea",
    "Coughing",
    "Labored_Breathing",
    "Lameness",
    "Skin_Lesions",
    "Nasal_Discharge",
    "Eye_Discharge",
    "Body_Temperature",
    "Heart_Rate"
]


X = df[FEATURES].copy()

y = df[TARGET]


# ============================================================
# YES / NO → 1 / 0
# ============================================================

print("\nConverting Yes/No health indicators...")

binary_columns = [
    "Appetite_Loss",
    "Vomiting",
    "Diarrhea",
    "Coughing",
    "Labored_Breathing",
    "Lameness",
    "Skin_Lesions",
    "Nasal_Discharge",
    "Eye_Discharge"
]


for column in binary_columns:

    X[column] = (
        X[column]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace(
            {
                "yes": 1,
                "no": 0,
                "true": 1,
                "false": 0
            }
        )
    )

    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )


# ============================================================
# CLEAN NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Age",
    "Weight",
    "Heart_Rate"
]


for column in numeric_columns:

    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )


# ============================================================
# CLEAN BODY TEMPERATURE
# ============================================================

print(
    "Cleaning body temperature values..."
)

X["Body_Temperature"] = (
    X["Body_Temperature"]
    .astype(str)
    .str.replace(
        "°C",
        "",
        regex=False
    )
    .str.replace(
        "Â",
        "",
        regex=False
    )
    .str.strip()
)

X["Body_Temperature"] = pd.to_numeric(
    X["Body_Temperature"],
    errors="coerce"
)


# ============================================================
# CLEAN DURATION
# ============================================================

# Duration is treated as categorical because
# the original model was trained this way.

X["Duration"] = (
    X["Duration"]
    .astype(str)
    .str.strip()
)


# ============================================================
# COLUMN TYPES
# ============================================================

categorical_features = [
    "Animal_Type",
    "Breed",
    "Gender",
    "Symptom_1",
    "Symptom_2",
    "Symptom_3",
    "Symptom_4",
    "Duration"
]


numeric_features = [
    "Age",
    "Weight",
    "Appetite_Loss",
    "Vomiting",
    "Diarrhea",
    "Coughing",
    "Labored_Breathing",
    "Lameness",
    "Skin_Lesions",
    "Nasal_Discharge",
    "Eye_Discharge",
    "Body_Temperature",
    "Heart_Rate"
]


# ============================================================
# PREPROCESSING
# ============================================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        ),
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        )
    ]
)


# ============================================================
# RANDOM FOREST
# ============================================================

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=RANDOM_STATE
)


# ============================================================
# COMPLETE PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessing",
            preprocessor
        ),
        (
            "model",
            model
        )
    ]
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y
    )
)


print("\n===== DATA SPLIT =====")

print(
    "Training records:",
    len(X_train)
)

print(
    "Testing records:",
    len(X_test)
)


# ============================================================
# TRAIN
# ============================================================

print("\nTraining Random Forest...")

pipeline.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTIONS
# ============================================================

predictions = pipeline.predict(
    X_test
)


# ============================================================
# ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions
)


print("\n==============================================")
print("             MODEL PERFORMANCE")
print("==============================================")

print(
    "Accuracy:",
    round(
        accuracy * 100,
        2
    ),
    "%"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n===== CLASSIFICATION REPORT =====")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# ============================================================
# BACKUP OLD MODEL
# ============================================================

if os.path.exists(MODEL_PATH):

    print(
        "\nBacking up existing model..."
    )

    shutil.copy2(
        MODEL_PATH,
        BACKUP_MODEL_PATH
    )

    print(
        "Backup saved to:",
        BACKUP_MODEL_PATH
    )


# ============================================================
# SAVE NEW MODEL
# ============================================================

joblib.dump(
    pipeline,
    MODEL_PATH
)


print(
    "\nNew model saved to:"
)

print(
    MODEL_PATH
)


# ============================================================
# FINAL INFORMATION
# ============================================================

print("\n==============================================")
print("             TRAINING COMPLETE")
print("==============================================")

print(
    "Training classes:",
    len(valid_diseases)
)

print(
    "Training records:",
    len(df)
)

print(
    "FMD records after normalization:",
    disease_counts.get(
        "Foot-and-Mouth Disease",
        0
    )
)

print(
    "\nThe new clinical model is ready."
)