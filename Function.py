import plotly as plt
import pandas as pd
import requests
import pytz

def from_utc_israel(utc_time):
    utc = pytz.utc
    israel = pytz.timezone('Asia/Jerusalem')
    utc_time_local = utc.localize(utc_time)
    local_time = utc_time_local.astimezone(israel)
    return local_time

def get_historical_data(symbol,start_date,end_date,key_code):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&symbol={symbol}&apikey={key_code}'
    res = requests.get(url)
    data = res.json()
    dict_data = data.get('Time Series (Daily)')
    df = pd.DataFrame.from_dict(dict_data, orient='index').astype(float)
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df['Daily_change_percent'] = round(df['close'].pct_change(),2)
    result_df = df.loc[start_date:end_date]

    return result_df

def data_today(symbol,key_code):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={key_code}'
    res = requests.get(url)
    data = res.json()
    data_symbol = data["Global Quote"]
    last_price = data_symbol["05. price"]
    previous_price = data_symbol["08. previous close"]
    chg_day = data_symbol["10. change percent"]
    return last_price,previous_price,chg_day

