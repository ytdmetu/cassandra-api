from fastapi import FastAPI, HTTPException, status
from model import HistoryInput, ForecastInput
import yfinance as yf
from datetime import date

from cassandra.forecast import ForecastStrategy, forecast


api = FastAPI()


@api.get("/history")
def get_stock_prices(data: HistoryInput):
    if data.start_date > data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date",
        )
    if data.end_date > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be before today",
        )
    hist = (
        yf.Ticker(data.stock)
        .history(start=data.start_date, end=data.end_date, interval=data.interval)
        .reset_index()
        .to_dict(orient="records")
    )
    return hist


@api.post("/forecast")
def get_stock_prices(data: ForecastInput):
    if data.start_date > data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date",
        )
    if data.end_date > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be before today",
        )
    df = yf.Ticker(data.stock).history(
        start=data.start_date, end=data.end_date, interval=data.interval
    )
    strategy = data.strategy or ForecastStrategy.naive_lstm
    predictions = forecast(data.stock, df, strategy=strategy)
    return predictions
