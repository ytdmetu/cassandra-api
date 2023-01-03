stocklist=["META","AAPL"]
strategylist=["gaussian","random_walk","naive_forecast","multivariate_diff"]

def forecast_test():
      forecast_endpoint = 'https://cassandra-api.herokuapp.com/forecast'
      for i in stocklist:
        for k in strategylist:
          payload = {
          
          "stock": i,
          "start_date": "2022-11-02",
          "end_date": "2022-11-09",
          "interval": "1h",
          "n_forecast": 12,
          "strategy": k}
          res = requests.post(forecast_endpoint, json=payload)
          res_body = res.json()
          assert res.status_code == 200
            

def test_forecast_past_hour():
    forecast_endpoint = 'https://cassandra-api.herokuapp.com/forecast_past_hours'
    for i in stocklist:
        for k in strategylist:
          payload = {
          "stock": i,
          "start_date": "2022-11-01",
          "end_date": "2022-11-02",
          "interval": "1h",
          "n_forecast": 10,
          "strategy": k
      }
          res = requests.post(forecast_endpoint, json=payload)
          res_body = res.json()
          assert res.status_code == 200
