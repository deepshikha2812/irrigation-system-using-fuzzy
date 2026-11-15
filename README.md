# Smart Plant Irrigation System

A web app that uses soil moisture, temperature, and humidity to estimate an irrigation level (0–100%), category, and recommendation.

## Model and data
- **Model:** Hand-written Mamdani fuzzy inference system with 17 rules and centroid defuzzification.
- **Dataset:** No dataset is used; membership ranges and rules are project assumptions, not plant-specific or scientifically calibrated advice.

## Tools
Python, FastAPI, SQLite, React, Vite, Recharts, and pytest.

## Key files
- `backend/app/main.py`: Creates the FastAPI app and defines its API endpoints, connecting requests to the fuzzy engine and stored predictions.
- `backend/tests/`: Pytest tests that check the API and fuzzy-logic behavior, including expected results and input validation.

## Run
Backend (from `backend/`): `uvicorn app.main:app --reload`  
Frontend (from `frontend/`): `npm install && npm run dev`  
Tests (from `backend/`): `python -m pytest -v`
