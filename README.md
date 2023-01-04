# Cassandra API

  Preconditions:
* Python3
* Pip3

Firstly, create an Python environment and activate it. Then install project dependencies.

```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

Then go inside /api folder. And run tests by 
```
pytest test_api.py
```

In order to run API in local env:
```
uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Stock price history

GET: `/stockprice`

Body: 
```json
{
    "stock": "META",
    "start_date": "2022-10-26",
    "end_date": "2022-10-27",
    "interval": "1h"
}
```

For interval, the following values can be used:
* minute = '1m'
* half_hour = '30m'
* hour = '1h'
* day = '1d'
* week = '1wk'
* month = '1mo'

### Forecast

POST: `/forecast`

Body: 
```json
{
    "stock": "META",
    "start_date": "2022-10-01",
    "end_date": "2022-10-27",
    "interval": "1h",
    "n_forecast": 12,
    "strategy": "naive_forecast"
}
```
For strategy, the following values can be used:
* random_walk
* gaussian
* naive_forecast
* multivariate_diff

## Example usage of API
```py
import requests
forecast_endpoint = 'https://cassandra-api.herokuapp.com/forecast'
payload = {
    "stock": "META",
    "start_date": "2022-11-02",
    "end_date": "2022-11-09",
    "interval": "1h",
    "n_forecast": 12,
    "strategy": "naive_forecast"
}
auth = requests.auth.HTTPBasicAuth("demo", "demo_password123")
res = requests.post(forecast_endpoint, json=payload, auth=auth)
print(res.status_code)
print(res.json())
```
