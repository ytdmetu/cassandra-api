from app import app
from starlette.testclient import TestClient

test_client = TestClient(app)
test_client.auth = ('pytest', 'pytest')

def test_forecast_api():
    payload = {
        "stock": "AAPL",
        "start_date": "2022-11-01",
        "end_date": "2022-11-02",
        "interval": "1h",
        "n_forecast": 10,
        "strategy": "gaussian"
    }
    response = test_client.post("/forecast", json=payload)
    assert response.status_code == 200

def test_forecast_past_hour_api():
    payload = {
        "stock": "AAPL",
        "start_date": "2022-11-01",
        "end_date": "2022-11-02",
        "interval": "1h",
        "n_forecast": 10,
        "strategy": "gaussian"
    }
    response = test_client.post("/forecast_past_hours", json=payload)
    assert response.status_code == 200