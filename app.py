from fastapi import FastAPI, HTTPException, status
from model import HistoryInput, ForecastInput
import yfinance as yf
from datetime import date
import pandas as pd

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

    # Find time difference between start and end date in hours
    timediff = (data.end_date - data.start_date)
    timediff = timediff.days * 24 + timediff.seconds // 3600
    if timediff >= 24:
        new_predictions = []
        for i in range(12):
            new_df = df.iloc[:-(12-i)]
            strategy = data.strategy or ForecastStrategy.naive_lstm
            pred = forecast(data.stock, new_df, strategy=strategy)
            new_predictions.append(pred['y'][0])
        comparision_df = (df.reset_index().iloc[-12:].rename(columns={'index': 'Date', 'Close':'Actual'})[['Date', 'Actual']])
        comparision_df['Predicted'] = new_predictions
        comparisions = comparision_df.to_dict(orient='records')
        return predictions, comparisions
    else:
        return predictions
