from app.models import PatientData

def generate_recommendation(patient: PatientData) -> str:
    if patient.age > 65 and patient.has_chronic_pain:
        return "Physical Therapy"
    if patient.bmi > 30:
        return "Weight Management Program"
    if patient.recent_surgery:
        return "Post-Op Rehabilitation Plan"
    return "General Wellness Plan"
