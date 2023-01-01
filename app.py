import datetime
from functools import lru_cache

import pandas as pd
import yfinance as yf
from cassandra.forecast import ForecastStrategy, forecast, forecast_past
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, FastAPI, HTTPException
import json
from passlib.hash import pbkdf2_sha256
from model import ForecastInput, StockPrice

TIMEZONE = datetime.timezone.utc
FORECAST_INPUT_START_OFFSET = 30
api = FastAPI()

security = HTTPBasic()
def security_check(username: str, password: str):
    with open("users.json", "r") as f:
        users = json.load(f)
    try:
        if pbkdf2_sha256.verify(password, users.get(username)):
            return True
        else:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
    except:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

@api.get("/stockprice")
# Stock price history
def fetch_price(data: StockPrice, credentials: HTTPBasicCredentials = Depends(security)):
    security_check(credentials.username, credentials.password)
    # Stock price fetch from yfinance
    hist = (
        yf.Ticker(data.stock)
        .history(start=data.start_date, end=data.end_date, interval=data.interval)
        .reset_index()
        .to_dict(orient="records")
    )
    return hist


# Stock price history
@lru_cache(maxsize=10)
def fetch_stock_price(stock_id, start, end, interval="1h"):
    raw_df = (
        yf.Ticker(stock_id)
        .history(start=start, end=end, interval=interval)
        .tz_convert(TIMEZONE)
    )
    return pd.DataFrame(index=raw_df.index, data=dict(price=raw_df.Close.values))


@api.post("/forecast")
def get_stock_prices(data: ForecastInput, credentials: HTTPBasicCredentials = Depends(security)):
    security_check(credentials.username, credentials.password)
    n_forecast = data.n_forecast or 12
    # stock price history
    df = fetch_stock_price(
        data.stock, data.start_date.isoformat(), data.end_date.isoformat()
    )
    # forecast
    input_df = df[
        data.end_date - datetime.timedelta(days=FORECAST_INPUT_START_OFFSET) :
    ]
    forecast_data = forecast(
        data.strategy,
        data.stock,
        input_df,
        n_forecast,
    )
    past_predictions = forecast_past(data.strategy, df, data.stock)
    # representation
    history_data = {"x": df.index.tolist(), "y": df.price.tolist(), "name": "History"}
    forecast_data["name"] = "Forecast"
    past_predictions["name"] = "Backtest"
    forecast_data["x"].insert(0, history_data["x"][-1])
    forecast_data["y"].insert(0, history_data["y"][-1])
    return [history_data, forecast_data, past_predictions]


@api.post("/forecast_past_hours")
def forecast_past_hour(data: ForecastInput, credentials: HTTPBasicCredentials = Depends(security)):
    security_check(credentials.username, credentials.password)
    df = yf.Ticker(data.stock).history(
        start=data.start_date, end=data.end_date, interval=data.interval
    )
    strategy = data.strategy or ForecastStrategy.naive_lstm
    df = fetch_stock_price(
        data.stock, data.start_date.isoformat(), data.end_date.isoformat()
    )
    return forecast_past(strategy, df, data.stock, look_back=60)
