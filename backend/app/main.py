"""FastAPI application: the HTTP interface to the fuzzy engine."""
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine, get_db
from app.fuzzy_engine import calculate_irrigation
from app.membership_functions import describe_variables
from app.schemas import HistoryItem, PredictionRequest, PredictionResponse

app = FastAPI(
    title="Smart Plant Irrigation System",
    description="Academic demonstration of Mamdani fuzzy logic. Ranges and rules are "
                "project assumptions, not agronomic advice.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine) 


@app.get("/")
def health_check() -> dict:
    return {"status": "ok", "project": "Smart Plant Irrigation (Mamdani Fuzzy Logic)"}


@app.post("/api/irrigation/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    """Run the fuzzy engine; optionally save the result."""
    try:
        result = calculate_irrigation(request.soil_moisture, request.temperature, request.humidity)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    saved_id = None
    if request.save:
        row = models.Prediction(
            soil_moisture=request.soil_moisture,
            temperature=request.temperature,
            humidity=request.humidity,
            irrigation_level=result["irrigation_level"],
            irrigation_category=result["category"],
            recommendation=result["recommendation"],
        )
        db.add(row)
        db.commit()
        saved_id = row.id

    return {**result, "saved": request.save, "id": saved_id}


@app.get("/api/irrigation/history", response_model=list[HistoryItem])
def history(limit: int = Query(default=50, ge=1, le=500), db: Session = Depends(get_db)):
    """Most recent predictions first."""
    query = select(models.Prediction).order_by(models.Prediction.id.desc()).limit(limit)
    return db.scalars(query).all()


@app.get("/api/irrigation/membership-functions")
def membership_functions() -> dict:
    """Curve data of every fuzzy set (used by the frontend charts)."""
    return describe_variables()
