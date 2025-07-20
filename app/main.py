from fastapi import FastAPI, Depends
from app.models import PatientData, RecommendationResponse, UserCredentials
from app.auth import create_access_token, verify_token
from app.rules import generate_recommendation
from app.cache import init_redis, get_cache, set_cache
from app.database import init_db, save_recommendation, get_recommendation_by_id
from app.events import publish_event
from uuid import uuid4
from datetime import datetime
import json

app = FastAPI(title="Clinical Recommendation API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    await init_redis()
    await init_db()

@app.post("/login")
def login(credentials: UserCredentials):
    if credentials.username == "admin" and credentials.password == "password":
        token = create_access_token(credentials.username)
        return {"access_token": token}
    return {"error": "Invalid credentials"}

@app.post("/evaluate", response_model=RecommendationResponse)
async def evaluate(patient: PatientData, user=Depends(verify_token)):
    cache_key = f"recommendation:{patient.age}:{patient.bmi}:{patient.has_chronic_pain}:{patient.recent_surgery}"
    cached = await get_cache(cache_key)
    if cached:
        cached["patient_id"] = patient.patient_id
        cached["timestamp"] = datetime.utcnow()
        return cached


    recommendation = generate_recommendation(patient)
    rec_id = str(uuid4())
    timestamp = datetime.utcnow()

    record = {
        "recommendation_id": rec_id,
        "patient_id": patient.patient_id,
        "recommendation": recommendation,
        "timestamp": timestamp
    }

    await save_recommendation(record)
    await set_cache(cache_key, record)
    publish_event({
        "patient_id": patient.patient_id,
        "recommendation_id": rec_id,
        "recommendation": recommendation,
        "timestamp": timestamp.isoformat()
    })

    return record

@app.get("/recommendation/{rec_id}", response_model=RecommendationResponse)
async def get_recommendation(rec_id: str, user=Depends(verify_token)):
    rec = await get_recommendation_by_id(rec_id)
    if not rec:
        return {"error": "Recommendation not found"}
    return rec
