import os 

class Config(object):
    API_TOKEN_EODHD_1 = os.environ.get("API_TOKEN_EODHD_1")
    API_TOKEN_EODHD_2 = os.environ.get("API_TOKEN_EODHD_2")
    API_TOKEN_FINNHUB = os.environ.get("API_TOKEN_FINNHUB")
    API_TOKEN_MARKETAUX = os.environ.get("API_TOKEN_MARKETAUX")