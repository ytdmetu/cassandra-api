import datetime
import json

import pandas as pd
import requests
import yfinance as yf
from cassandra.forecast import ForecastStrategy, forecast, forecast_past
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from model import ForecastInput, StockPrice
from passlib.hash import pbkdf2_sha256

TIMEZONE = datetime.timezone.utc
FORECAST_INPUT_START_OFFSET = 15
app = FastAPI()


security = HTTPBasic()


def security_check(username: str, password: str):
    with open("users.json", "r") as f:
        users = json.load(f)
    try:
        if pbkdf2_sha256.verify(password, users.get(username)):
            return True
        else:
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
    except:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


@app.get("/stockprice")
# Stock price history
def fetch_price(
    data: StockPrice, credentials: HTTPBasicCredentials = Depends(security)
):
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
def fetch_stock_price(stock_id, start, end, interval="1h"):
    raw_df = (
        yf.Ticker(stock_id)
        .history(start=start, end=end, interval=interval)
        .tz_convert(TIMEZONE)
    )
    return pd.DataFrame(index=raw_df.index, data=dict(price=raw_df.Close.values))


def fetch_stock_price_n_news(stock_id, start, end, interval="1h"):
    from cassandra.sentiment import compute_sentiment_score

    timegroup = [
        datetime.datetime.strptime("14:30:00", "%H:%M:%S").time(),
        datetime.datetime.strptime("15:30:00", "%H:%M:%S").time(),
        datetime.datetime.strptime("16:30:00", "%H:%M:%S").time(),
        datetime.datetime.strptime("17:30:00", "%H:%M:%S").time(),
        datetime.datetime.strptime("18:30:00", "%H:%M:%S").time(),
        datetime.datetime.strptime("19:30:00", "%H:%M:%S").time(),
        datetime.datetime.strptime("20:30:00", "%H:%M:%S").time(),
    ]

    raw_df = (
        yf.Ticker(stock_id)
        .history(start=start, end=end, interval=interval)
        .tz_convert(TIMEZONE)
    )
    raw_df["timestamp"] = raw_df.index.astype("int64") // 10**9
    output = pd.DataFrame(
        requests.get(
            f"https://finnhub.io/api/v1/company-news?symbol={stock_id}&from={start}&to={end}&token=ceep5d2ad3i92ceb1ingceep5d2ad3i92ceb1io0"
        ).json()
    )
    output["datetime"] = output["datetime"].apply(
        lambda x: datetime.datetime.fromtimestamp(x)
    )
    output["sentiment"] = output["summary"].apply(lambda x: compute_sentiment_score(x))
    output["sentiment_group"] = output["sentiment"].apply(lambda x: x[0]["label"])
    output["sentiment_score"] = output["sentiment"].apply(lambda x: x[0]["score"])
    # datetime values in your column to the nearest half past hour.
    output["datetime_group"] = output["datetime"]
    output["time_group"] = output["datetime_group"].apply(
        lambda x: datetime.datetime.time(x)
    )
    output["time_group"] = output["time_group"].apply(
        lambda x: timegroup[0]
        if x <= timegroup[0]
        else timegroup[1]
        if x <= timegroup[1]
        else timegroup[2]
        if x <= timegroup[2]
        else timegroup[3]
        if x <= timegroup[3]
        else timegroup[4]
        if x <= timegroup[4]
        else timegroup[5]
        if x <= timegroup[5]
        else timegroup[5]
        if x <= timegroup[6]
        else x
    )
    output["date"] = output["datetime_group"].apply(lambda x: datetime.datetime.date(x))
    output["datetime_group"] = pd.to_datetime(
        output.date.astype(str) + " " + output.time_group.astype(str)
    )
    output["datetime_group"] = output["datetime_group"].apply(
        lambda x: datetime.datetime.timestamp(x)
    )
    sentiment_results = (
        output.groupby(["datetime_group", "sentiment_group"])["category"]
        .agg("count")
        .reset_index()
    )
    df_sentiment = (
        pd.DataFrame.from_dict(
            dict(
                zip(
                    sentiment_results["datetime_group"],
                    sentiment_results["sentiment_group"].apply(
                        lambda x: -1 if x == "negative" else 1 if x == "positive" else 0
                    )
                    * sentiment_results["category"],
                )
            ),
            orient="index",
            columns=["sentiment_score"],
        )
    )
    raw_df = raw_df.merge(
        df_sentiment,
        left_on="timestamp",
        right_index=True,
        how="left",
    ).fillna(0)
    return pd.DataFrame(
        index=raw_df.index,
        data=dict(
            price=raw_df.Close.values, sentiment_score=raw_df.sentiment_score.values
        ),
    )


@app.post("/forecast")
def get_stock_prices(
    data: ForecastInput, credentials: HTTPBasicCredentials = Depends(security)
):
    security_check(credentials.username, credentials.password)
    n_forecast = data.n_forecast or 12
    # stock price history
    if "nlp" in data.strategy:
        df = fetch_stock_price_n_news(
            data.stock, data.start_date.isoformat(), data.end_date.isoformat()
        )
    else:
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


@app.post("/forecast_past_hours")
def forecast_past_hour(
    data: ForecastInput, credentials: HTTPBasicCredentials = Depends(security)
):
    security_check(credentials.username, credentials.password)
    df = yf.Ticker(data.stock).history(
        start=data.start_date, end=data.end_date, interval=data.interval
    )
    strategy = data.strategy or ForecastStrategy.naive_lstm
    df = fetch_stock_price_n_news(
        data.stock, data.start_date.isoformat(), data.end_date.isoformat()
    )
    return forecast_past(strategy, df, data.stock, look_back=60)
