from datetime import date
from enum import Enum

from fastapi import HTTPException

from cassandra.forecast import ForecastStrategy
from pydantic import BaseModel, root_validator, validator


class Interval(str, Enum):
    minute = "1m"
    half_hour = "30m"
    hour = "1h"
    day = "1d"
    week = "1wk"
    month = "1mo"


class Stock(str, Enum):
    APPLE = "AAPL"
    META = "META"


class StockPrice(BaseModel):
    stock: Stock
    start_date: date
    end_date: date
    interval: Interval

    class Config:
        use_enum_values = True
        validate_assignment = True

    @validator("end_date")
    def end_date_not_in_future(cls, end_date):
        if end_date > date.today():
            raise HTTPException(status_code=400, detail='End date cannot be in future')
        return end_date

    @root_validator
    def start_date_before_end_date(cls, v):
        if v.get("start_date") > v.get("end_date"):
            raise HTTPException(status_code=400, detail='Start date must be before end date')
        return v


class ForecastInput(StockPrice):
    n_forecast: int
    strategy: ForecastStrategy
