import datetime
import pickle
from functools import lru_cache
from typing import List

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pandas.api.types import CategoricalDtype
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from tsai.inference import get_X_preds
from tsai.learner import load_learner

from ..features import prepare_dataset
from ..timeseries_utils import make_ts_samples
from ..utils import get_artifact_filepath


# Inference
class Forecaster:
    def __init__(self, xpp, ypp, learn, look_back):
        self.xpp = xpp
        self.ypp = ypp
        self.learn = learn
        self.look_back = look_back

    def __call__(self, df: pd.DataFrame, xnew: List[datetime.datetime]):
        n = len(xnew)
        initial_length = len(df)
        for i in range(n):
            pred = self._predict_one(df)
            df = add_prediction_to_dataset(df, pred)
        return df.price.values[initial_length:].tolist()

    def _predict_one(self, raw_df):
        df = prepare_dataset(raw_df.iloc[-self.look_back :])
        x_data_pp = self.xpp.transform(df)
        y_data_pp = self.ypp.transform(df["price_change"].values.reshape(-1, 1))
        data_pp = np.concatenate([x_data_pp, y_data_pp], axis=1)
        xb, _ = make_ts_samples(data_pp, self.look_back)
        _, _, y_pred = self.learn.get_X_preds(xb)
        price_change = self.ypp.inverse_transform(
            np.array(y_pred).reshape(-1, 1)
        ).item()
        return df.price[-1] + price_change


def add_prediction_to_dataset(df, price):
    next_datetime = df.index[-1] + pd.DateOffset(hours=1)
    new_df = pd.DataFrame(index=[next_datetime], data=dict(price=[price]))
    return pd.concat([df, new_df], axis=0)


def build_forecaster(
    x_preprocessor_filepath, y_preprocessor_filepath, learn_filepath, look_back
):
    learn = load_learner(learn_filepath)
    xpp = pickle.load(open(x_preprocessor_filepath, "rb"))
    ypp = pickle.load(open(y_preprocessor_filepath, "rb"))
    forecaster = Forecaster(xpp, ypp, learn, look_back)
    return forecaster


@lru_cache(maxsize=1)
def get_meta_forecaster():
    print("Creating LSTM model for META")
    return build_forecaster(
        get_artifact_filepath("meta/multivariate-diff/xpp.pkl"),
        get_artifact_filepath("meta/multivariate-diff/ypp.pkl"),
        get_artifact_filepath("meta/multivariate-diff/learn.pkl"),
        look_back=60,
    )


@lru_cache(maxsize=1)
def get_aapl_forecaster():
    print("Creating LSTM model for AAPL")
    return build_forecaster(
        get_artifact_filepath("aapl/multivariate-diff/xpp.pkl"),
        get_artifact_filepath("aapl/multivariate-diff/ypp.pkl"),
        get_artifact_filepath("aapl/multivariate-diff/learn.pkl"),
        look_back=60,
    )


def forecast(stock_id, df, xnew):
    if stock_id.lower() == "meta":
        return get_meta_forecaster()(df, xnew)
    if stock_id.lower() == "aapl":
        return get_aapl_forecaster()(df, xnew)
    raise ValueError()


# warmup
get_meta_forecaster()
