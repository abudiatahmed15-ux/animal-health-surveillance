from pydantic import BaseModel, Field
from typing import Optional


class AnimalCase(BaseModel):

    Animal_Type: str = Field(
        ...,
        description="Type of livestock, e.g. Cow, Goat, Sheep"
    )

    Breed: str = Field(
        ...,
        description="Breed of the animal"
    )

    Age: float = Field(
        ...,
        ge=0,
        description="Animal age in years"
    )

    Gender: str = Field(
        ...,
        description="Male or Female"
    )

    Weight: float = Field(
        ...,
        gt=0,
        description="Animal weight in kg"
    )

    Symptom_1: str = Field(
        ...,
        description="Primary symptom"
    )

    Symptom_2: str = Field(
        ...,
        description="Secondary symptom"
    )

    Symptom_3: str = Field(
        ...,
        description="Third symptom"
    )

    Symptom_4: str = Field(
        ...,
        description="Fourth symptom"
    )

    Duration: str = Field(
        ...,
        description="Duration of symptoms"
    )

    Appetite_Loss: str = Field(
        ...,
        description="Yes or No"
    )

    Vomiting: str = Field(
        ...,
        description="Yes or No"
    )

    Diarrhea: str = Field(
        ...,
        description="Yes or No"
    )

    Coughing: str = Field(
        ...,
        description="Yes or No"
    )

    Labored_Breathing: str = Field(
        ...,
        description="Yes or No"
    )

    Lameness: str = Field(
        ...,
        description="Yes or No"
    )

    Skin_Lesions: str = Field(
        ...,
        description="Yes or No"
    )

    Nasal_Discharge: str = Field(
        ...,
        description="Yes or No"
    )

    Eye_Discharge: str = Field(
        ...,
        description="Yes or No"
    )

    Body_Temperature: float = Field(
        ...,
        description="Body temperature in Celsius"
    )

    Heart_Rate: float = Field(
        ...,
        gt=0,
        description="Heart rate in beats per minute"
    )

    District: str = Field(
        ...,
        description="Maharashtra district"
    )