import numpy as np
import datetime
from enum import Enum
from random import random

from .lstm_stock_price_forecast import build_forecaster
from .utils import get_asset_filepath


class ForecastStrategy(str, Enum):
    gaussian = "gaussian"
    random_walk = "random_walk"
    naive_lstm = "naive_lstm"


def gaussian_noise(x, n=12):
    return x.mean() + x.std() * 10 * np.random.rand(n)


def random_walk(x, n=12):
    initial_value = x[-1]
    delta = x.std()
    result = [initial_value]
    for i in range(1, n):
        movement = -delta if random() < 0.5 else delta
        value = result[i - 1] + movement
        result.append(value)
    return result[1:]


lstm_forecaster_config = dict(
    data=dict(
        look_back=60,
    ),
    model=dict(
        input_dim=1,
        hidden_dim=32,
        num_layers=2,
        output_dim=1,
    ),
    inference=dict(),
)

lstm_forecaster = build_forecaster(
    lstm_forecaster_config,
    get_asset_filepath("preprocessor.pkl"),
    get_asset_filepath("model.pth"),
)


def lstm_forecast(x, n=12):
    look_back = lstm_forecaster_config["data"]["look_back"]
    return lstm_forecaster(x[-look_back:], n)


def forecast(stock_id, df, n_forecast=12, strategy=ForecastStrategy.random_walk):
    start_time = df.index[-1].to_pydatetime()
    x = [start_time + datetime.timedelta(hours=i) for i in range(1, 1 + n_forecast)]
    if strategy == ForecastStrategy.gaussian:
        y = gaussian_noise(df.Close.values).tolist()
    elif strategy == ForecastStrategy.random_walk:
        y = random_walk(df.Close.values)
    elif strategy == ForecastStrategy.naive_lstm:
        y = lstm_forecast(df.Close.values)
    else:
        raise ValueError(strategy)
    return dict(x=x, y=y)
