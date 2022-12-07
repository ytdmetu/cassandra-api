from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum
from cassandra.forecast import ForecastStrategy


class Interval(str, Enum):
    minute = "1m"
    half_hour = "30m"
    hour = "1h"
    day = "1d"
    week = "1wk"
    month = "1mo"


class HistoryInput(BaseModel):
    stock: str
    start_date: date
    end_date: date
    interval: Interval

    class Config:
        use_enum_values = True


class ForecastInput(BaseModel):
    stock: str
    start_date: date
    end_date: date
    interval: Interval
    n_forecast: int
    strategy: ForecastStrategy

    class Config:
        use_enum_values = True
