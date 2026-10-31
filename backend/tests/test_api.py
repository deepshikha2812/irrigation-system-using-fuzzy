import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    """Test client that uses a throw-away in-memory database."""
    test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                                poolclass=StaticPool)
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine, autoflush=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_check(client):
    assert client.get("/").json()["status"] == "ok"


def test_predict_returns_fuzzy_analysis(client):
    response = client.post("/api/irrigation/predict",
                           json={"soil_moisture": 28, "temperature": 34, "humidity": 40})
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["irrigation_level"] <= 100
    assert body["category"] in ("Very Low", "Low", "Medium", "High", "Very High")
    assert set(body["membership_values"]["soil_moisture"]) == {"dry", "medium", "wet"}
    assert body["saved"] is True and body["id"] == 1


def test_prediction_is_saved_and_listed_newest_first(client):
    client.post("/api/irrigation/predict", json={"soil_moisture": 20, "temperature": 35, "humidity": 30})
    client.post("/api/irrigation/predict", json={"soil_moisture": 80, "temperature": 25, "humidity": 70})
    history = client.get("/api/irrigation/history").json()
    assert [row["id"] for row in history] == [2, 1]
    assert history[0]["soil_moisture"] == 80
    assert history[0]["irrigation_category"] == "Very Low"


def test_save_false_does_not_store(client):
    response = client.post("/api/irrigation/predict", json={
        "soil_moisture": 50, "temperature": 25, "humidity": 50, "save": False})
    assert response.json()["saved"] is False
    assert client.get("/api/irrigation/history").json() == []


def test_history_limit(client):
    for _ in range(3):
        client.post("/api/irrigation/predict", json={"soil_moisture": 50, "temperature": 25, "humidity": 50})
    assert len(client.get("/api/irrigation/history?limit=2").json()) == 2


@pytest.mark.parametrize("payload", [
    {"soil_moisture": 101, "temperature": 25, "humidity": 50},
    {"soil_moisture": -5, "temperature": 25, "humidity": 50},
    {"soil_moisture": 50, "temperature": 60, "humidity": 50},
    {"soil_moisture": 50, "temperature": 25, "humidity": 120},
    {"soil_moisture": "abc", "temperature": 25, "humidity": 50},
    {"soil_moisture": 50, "temperature": 25},
])
def test_invalid_input_returns_422(client, payload):
    response = client.post("/api/irrigation/predict", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_invalid_request_is_not_saved(client):
    client.post("/api/irrigation/predict", json={"soil_moisture": 500, "temperature": 25, "humidity": 50})
    assert client.get("/api/irrigation/history").json() == []


def test_membership_function_endpoint(client):
    body = client.get("/api/irrigation/membership-functions").json()
    assert set(body) == {"soil_moisture", "temperature", "humidity", "irrigation"}
    assert len(body["irrigation"]["sets"]) == 5
