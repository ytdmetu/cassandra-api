from fastapi import FastAPI, HTTPException, status
from model import HistoryInput, ForecastInput, NewsInput
import yfinance as yf
from datetime import date, timedelta
import requests
from cassandra.forecast import ForecastStrategy, forecast, forecast_past_hours
import random

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

@api.post("/forecast_past_hours")
def forecast_past_hour(data: ForecastInput):
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

    comparisions = forecast_past_hours(data.start_date, data.end_date, df, strategy, data.stock)
    return comparisions

@api.get('/news')
def get_news(data: NewsInput):
    random_number = random.randint(1, 3)
    # TODO: ustteki siteden gunluk maks 20 haber (request degil haber sayisi) cekilebiliyor. Bu yuzden simdilik o tarafa istek atilmiyor. 
    # Usttekinin avantaji haberin semantic sonucunu da donduruyor.
    if random_number < 1:
        if data.symbol == 'AAPL':
            api_token = 'demo'
        else:
            # print random number between 1 and 100
            rand = random.randint(1, 2)
            if rand == 1:
                api_token = '638cbb941b1ef2.16325735'
            else:
                api_token = '638cbfbf6589f9.48995036'
        url = f"https://eodhistoricaldata.com/api/news?api_token={api_token}&s={data.symbol}&offset=0&limit=10"
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        
        return response.json()
    else:
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() + timedelta(days=1)
        url = f"https://finnhub.io/api/v1/company-news?symbol={data.symbol}&from={start_date}&to={end_date}&token=ce6c09qad3i7uksh7co0ce6c09qad3i7uksh7cog"
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return (response.json())

