import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import app.cache as cache
import asyncio


class DummyRedis:
    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ex=None):
        self.store[key] = value

# Override the redis instance for tests
cache.redis = DummyRedis()


@pytest.mark.asyncio
async def test_login_and_evaluate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/login", json={"username": "admin", "password": "password"})
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        patient = {
            "patient_id": 1,
            "age": 70,
            "bmi": 28,
            "has_chronic_pain": True,
            "recent_surgery": False
        }
        response = await ac.post("/evaluate", json=patient, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient["patient_id"]
        assert data["recommendation"] == "Physical Therapy"
        rec_id = data["recommendation_id"]

        response = await ac.get(f"/recommendation/{rec_id}", headers=headers)
        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["recommendation_id"] == rec_id
        assert retrieved["recommendation"] == "Physical Therapy"

@pytest.mark.asyncio
async def test_invalid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        patient = {
            "patient_id": 2,
            "age": 50,
            "bmi": 32,
            "has_chronic_pain": False,
            "recent_surgery": False
        }
        response = await ac.post("/evaluate", json=patient, headers={"Authorization": "Bearer wrongtoken"})
        assert response.status_code == 401
