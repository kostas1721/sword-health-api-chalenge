import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta

SECRET_KEY = "secret"
ALGORITHM = "HS256"
security = HTTPBearer()

def create_access_token(username: str):
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials=Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
