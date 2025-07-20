# sword-health-api-chalenge
This project implements a scalable, event-driven Clinical Recommendation API using Python, FastAPI, PostgreSQL, Redis for caching and event-driven notifications. The entire system is containerized using Docker and orchestrated via docker-compose.

# Setup and Run
Clone repo

cd sword-health-api-chalenge

docker-compose up --build

You can find the OPEN API docs at: http://localhost:8000/docs

# API Endpoints example requests
- Authenticate:
- 
  curl -X POST "http://localhost:8000/login" \
            -H "Content-Type: application/json" \
            -d '{"username": "admin", "password": "password"}'
- Evaluate:

  curl -X POST "http://localhost:8000/evaluate" \
            -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{
                "patient_id": 24,
                "age": 44,
                "bmi": 18,
                "has_chronic_pain": false,
                "recent_surgery": true
            }'
- Recommendation by ID:

  curl -X GET "http://localhost:8000/recommendation/<YOUR_RECOMENDATION_ID>" \
            -H "Authorization: Bearer <YOUR_JWT_TOKEN>"

# Example Responses
- Authenticate:

  {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MzAzMDEzMn0.JFav9baPvrCqRLCxTnBp8u1HQrLGibpeh8m-hQtwZBY"}

- Evaluate:

  {"recommendation_id":"50a5b58a-b4ac-4908-83ea-6a66bef2f3aa","patient_id":24,"recommendation":"Post-Op Rehabilitation Plan","timestamp":"2025-07-20T15:49:19.601402"}

- Recommendation by ID:

  {"recommendation_id":"f57f3f14-ea74-4512-a0f9-fc982ae5d051","patient_id":4,"recommendation":"Post-Op Rehabilitation Plan","timestamp":"2025-07-20T14:48:36.748036"}

# Automated Tests
In this project there are some simple automated tests to ensure the basic functionality.

Thee are 3 automated test:

- test_login_and_evaluate: Tests the authentication and then the /evaluate endpoint
- test_invalid_token: Tests the response we get when having an invalid token
- test_recommendation_by_id: Tests the get recommendation by ID


To run the you have to get in container:

docker exec -it sword-health-api-chalenge-api-1 bash

And then run:

pytest -v tests/test_api.py

# Testing Proof
All Testing Proof and guidance can be found in the Testing_Guide_And_Proof file.
Through this file we can ensure that the Caching works as expected, the recomendation generated is published to the message Broker (Redis Pub/Sub), the consumer (worker.py) logs the recommendations to the DB and a logfile and finaly the concurrent request handling capabilities.
