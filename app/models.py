
from pydantic import BaseModel
from datetime import datetime

class PatientData(BaseModel):
    patient_id: int
    age: int
    bmi: float
    has_chronic_pain: bool = False
    recent_surgery: bool = False

class RecommendationResponse(BaseModel):
    recommendation_id: str
    patient_id: int
    recommendation: str
    timestamp: datetime

class UserCredentials(BaseModel):
    username: str
    password: str
