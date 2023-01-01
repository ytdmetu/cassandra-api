import datetime
from functools import lru_cache

import pandas as pd
import yfinance as yf
from cassandra.forecast import ForecastStrategy, forecast, forecast_past
from fastapi import FastAPI, HTTPException, status
from model import ForecastInput, StockPrice

TIMEZONE = datetime.timezone.utc
FORECAST_INPUT_START_OFFSET = 30
api = FastAPI()


def validate_dates(start_date, end_date):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date",
        )
    if end_date > datetime.date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be before today",
        )
    return True


@api.get("/stockprice")
# Stock price history
def fetch_price(data: StockPrice):
    # Stock price fetch from yfinance
    validate_dates(data.start_date, data.end_date)
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
def get_stock_prices(data: ForecastInput):
    validate_dates(data.start_date, data.end_date)
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
def forecast_past_hour(data: ForecastInput):
    validate_dates(data.start_date, data.end_date)
    df = yf.Ticker(data.stock).history(
        start=data.start_date, end=data.end_date, interval=data.interval
    )
    strategy = data.strategy or ForecastStrategy.naive_lstm
    df = fetch_stock_price(
        data.stock, data.start_date.isoformat(), data.end_date.isoformat()
    )
    return forecast_past(strategy, df, data.stock, look_back=60)
