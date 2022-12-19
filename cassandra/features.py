import datetime

import holidays
import pandas as pd


def is_us_holiday(dt):
    return dt.strftime("%Y-%m-%d") in holidays.UnitedStates()


def extract_datetime_features(ds):
    df = pd.DataFrame()
    df.index = ds
    df["day"] = ds.day
    df["hour"] = ds.hour
    df["month_name"] = ds.month_name()
    df["day_name"] = ds.day_name()
    df["is_weekend"] = (ds.day_name() == 'Saturday') | (ds.day_of_week == 'Sunday')
    df["is_month_start"] = ds.is_month_start
    df["is_month_end"] = ds.is_month_end
    df["is_quarter_start"] = ds.is_quarter_start
    df["is_year_start"] = ds.is_year_start
    # US holidays
    df["is_holiday"] = pd.Series(ds.values).apply(is_us_holiday).values
    df["is_day_before_holiday"] = [is_us_holiday(dt) for dt in pd.Series(ds + datetime.timedelta(days=1)).tolist()]
    df["is_day_after_holiday"] = [is_us_holiday(dt) for dt in pd.Series(ds - datetime.timedelta(days=1)).tolist()]
    nominals = [
        "hour",
        "day",
        "day_name",
        "month_name",
        "is_weekend",
        "is_month_start",
        "is_month_end",
        "is_quarter_start",
        "is_year_start",
        "is_holiday",
        "is_day_before_holiday",
        "is_day_after_holiday",
    ]
    for col in nominals:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


def add_datetime_features(df):
    return pd.concat([extract_datetime_features(df.index), df], axis=1)


def add_price_change(df):
    df["price_change"] = df.price.diff().fillna(0)
    return df


def order_cols(df):
    categorical_cols = df.select_dtypes("category").columns.tolist()
    numerical_cols = df.select_dtypes("float").columns.tolist()
    existing_cols = set(df.columns)
    col_order = [
        col for col in numerical_cols + categorical_cols if col in existing_cols
    ]
    return df[col_order]


def prepare_dataset(df):
    return df.pipe(add_datetime_features).pipe(add_price_change).pipe(order_cols)
