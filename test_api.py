from app import api
from starlette.testclient import TestClient

test_client = TestClient(api)

def test_api():
    payload = {'stock': 'AAPL', 'start_date': '2021-01-01', 'end_date': '2021-01-02', 'is_hourly': False}
    response = test_client.post("/get_daily_data/", json=payload)
    assert response.status_code == 200