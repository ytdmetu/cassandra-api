from config import Config
import random
from datetime import date, timedelta
import requests

def get_news(symbol):
    random_number = random.randint(1, 3)
    # TODO: ustteki siteden gunluk maks 20 haber (request degil haber sayisi) cekilebiliyor. Bu yuzden simdilik o tarafa istek atilmiyor. 
    # Usttekinin avantaji haberin semantic sonucunu da donduruyor.
    if random_number < 1:
        if symbol == 'AAPL':
            api_token = 'demo'
        else:
            # print random number between 1 and 100
            rand = random.randint(1, 2)
            if rand == 1:
                api_token = Config.API_TOKEN1
            else:
                api_token = Config.API_TOKEN2
        url = f"https://eodhistoricaldata.com/api/news?api_token={api_token}&s={symbol}&offset=0&limit=10"
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        
        return response.json()
    else:
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() + timedelta(days=1)
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={start_date}&to={end_date}&token={Config.API_TOKEN3}"
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return (response.json())