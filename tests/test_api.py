import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import app.cache as cache

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


@pytest.mark.asyncio
async def test_recommendation_by_id(monkeypatch):
    # Stubbed recommendation that the DB would return
    fake_rec = {
        "recommendation_id": "f57f3f14-ea74-4512-a0f9-fc982ae5d051",
        "patient_id": 42,
        "recommendation": "Post-Op Rehabilitation Plan",
        "timestamp": "2025-07-20T14:48:36.748036"
    }

    # Patch the DB function so it returns the stub
    async def fake_get_recommendation_by_id(rec_id):
        return fake_rec

    monkeypatch.setattr("app.main.get_recommendation_by_id", fake_get_recommendation_by_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Login first to get a valid token
        response = await ac.post("/login", json={"username": "admin", "password": "password"})
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Call the endpoint
        response = await ac.get("/recommendation/123", headers=headers)
        assert response.status_code == 200
        data = response.json()

        # Verify the stubbed data is returned
        assert data["patient_id"] == fake_rec["patient_id"]
        assert data["recommendation"] == fake_rec["recommendation"]
        assert data["timestamp"] == fake_rec["timestamp"]