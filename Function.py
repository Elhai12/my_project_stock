import plotly as plt
import pandas as pd
import requests
import pytz
import yfinance as yf
import streamlit as st
import plotly.express as px

def from_utc_israel(utc_time):
    utc = pytz.utc
    israel = pytz.timezone('Asia/Jerusalem')
    utc_time_local = utc.localize(utc_time)
    local_time = utc_time_local.astimezone(israel)
    return local_time

def check_valid_tiker(info_stock):

    try:
        sym = info_stock.info['symbol']
        tiker_check_test = 'Valid'
        return tiker_check_test
    except Exception as er:
        if str(er) == "'symbol'":
            st.warning("The symbol not valid")
            tiker_check_test = 'Invalid'
        else:
            st.warning(f"Error: {er}")
            tiker_check_test = 'Valid'
        return tiker_check_test


def meta_fund_data(info_stock):
    info_stock = info_stock.info
    metadata_cols = [
        "shortName", "longName", "exchange", "currency", "sector",
        "industry", "country", "website",'longBusinessSummary']

    fundamentals_cols = [
        "marketCap", "enterpriseValue", "trailingPE", "forwardPE","bookValue", "dividendYield",
        "dividendRate", "ebitda", "totalRevenue","revenuePerShare", "freeCashflow", "operatingCashflow",
        "currentRatio", "quickRatio", "debtToEquity"]
    df_meta_data = pd.DataFrame.from_dict(info_stock,orient='index').T[metadata_cols].reset_index(drop=True).reset_index(drop=True)
    df_fundamentals = pd.DataFrame.from_dict(info_stock,orient='index').T[fundamentals_cols].reset_index(drop=True).reset_index(drop=True).map(lambda x: round(x, 2))

    return df_meta_data,df_fundamentals

def check_api(url):
    try:
        res = requests.get(url)
        err = None
        if res.status_code != 200 or 'API rate limit is' in res.text:
            err = "The credits required to make an additional query are insufficient. Please try again later"
            res = None
    except Exception as ex:
        err = f"Error: {ex}"
        res = None
    return  res,err

#I decided to drop this function in favor of using yfinance for historical data
# def get_historical_data(tiker,start_date,end_date,key_code):
#     url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&symbol={tiker}&apikey={key_code}'
#     res,err = check_api(url)
#     if res:
#         data = res.json()
#         dict_data = data.get('Time Series (Daily)')
#         df = pd.DataFrame.from_dict(dict_data, orient='index').astype(float)
#         df.columns = ['open', 'high', 'low', 'close', 'volume']
#         df.index = pd.to_datetime(df.index)
#         df = df.sort_index()
#         df['Daily_change_percent'] = round(df['close'].pct_change(),2)
#         result_df = df.loc[start_date:end_date]
#
#         return result_df
#     else:
#         st.warning(err)
#         return None


# def data_today(tiker,key_code):
#     url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={tiker}&apikey={key_code}'
#     res,err = check_api(url)
#     if res:
#         data = res.json()
#         data_tiker = data["Global Quote"]
#         last_price = data_tiker["05. price"]
#         previous_price = data_tiker["08. previous close"]
#         chg_day = data_tiker["10. change percent"]
#         list_data = last_price,previous_price,chg_day
#         return list_data
#     else:
#         st.warning(err)
#         return None

def real_data(info_stock):

    df_day = info_stock.history(period='1d',interval='1m')
    last_price = df_day['Close'].iloc[-1]
    last_time = df_day.index[-1]
    previous_price = info_stock.info['previousClose']
    chg_day = ((last_price/previous_price)-1) *100
    list_real_data = [last_price,previous_price,chg_day]
    return  list_real_data



def format_value_chg (chg_day_org):
    chg_day = str(round(chg_day_org, 2)) + "%"
    if chg_day.startswith("-"):
        formatted_value = f'<span style="color:red;">&#x2193; {chg_day}</span>'
    else:
        formatted_value = f'<span style="color:green;">&#x2191; {chg_day}</span>'
    return  formatted_value

def real_list(list_stock):
    dict_stocks = {}
    for tiker in list_stock:
        tiker_info = yf.Ticker(tiker)
        list_real = real_data(tiker_info)
        dict_stocks[tiker] = [list_real[0],format_value_chg(list_real[2])]
    for tiker in dict_stocks:
        st.write(tiker)
        col_1,col_2 = st.columns([1,1])
        with col_1:
            st.metric(label= "",value= round(dict_stocks[tiker][0],2))
        with col_2:
            st.markdown(f"{dict_stocks[tiker][1]}", unsafe_allow_html=True)
    return







def create_history_df_yf(info_stock,start,end):

    tiker = info_stock.info['symbol']
    df_history = info_stock.history(start=start, end=end, interval='1d')
    df_history = df_history.reindex(pd.date_range(start=df_history.index.min(), end=df_history.index.max(), freq='D'))
    df_history['Date'] = pd.to_datetime(df_history.index)

    df_history['year'] = df_history['Date'].dt.year

    df_history[['Open','High','Low','Close','Volume']] = df_history[['Open','High','Low','Close','Volume']].ffill()
    df_history['Daily_change_percent'] = df_history['Close'].pct_change()
    df_history['chg_month'] = df_history['Close'].pct_change(periods=30)
    df_history['symbol'] = tiker
    df_history['Cumulative_Return'] = (1 + df_history['Daily_change_percent']).cumprod() - 1
    df_history.index = pd.to_datetime(df_history.index).date


    return df_history

def create_plot(tiker,history_df,type_plot,index_df=None):

    df_fill = history_df.reindex(pd.date_range(start=history_df.index.min(), end=history_df.index.max(), freq='D'))
    df_fill['Close'] = df_fill['Close'].ffill()
    df_fill['chg_month'] = round(df_fill['Close'].pct_change(periods=30),2)
    df_fill['Date'] = pd.to_datetime(df_fill.index)
    df_fill['year'] = df_fill['Date'].dt.year
    df_fill.index = df_fill.index.floor('D')

    if type_plot == 'box':
        fig_day = px.box(df_fill,x='year',y='Daily_change_percent',title=f"Box plot for daily change percent compare years for {tiker}",
                         labels={'Daily_change_percent':'Daily change percent'})
        fig_month = px.box(df_fill,x='year',y='chg_month',title=f"Box plot for monthly change percent compare years for {tiker}",
                           labels={'chg_month':'Monthly change percent'})
        return fig_day,fig_month

    elif type_plot == 'line':
        fig_line = px.line(df_fill, x="Date", y="Close", title=f'Price close over time for {tiker}',labels={"Close": "Close Price"})
        return fig_line

    elif type_plot == 'compare':
        index_sym = index_df.symbol.max()
        df_fill['symbol'] = tiker
        df_concat = pd.concat([df_fill,index_df],axis=0)
        fig_compare = px.line(df_concat,x='Date',y='Cumulative_Return',color='symbol',title=f'Compare Daily change {tiker} vs {index_sym}'
                              ,labels={'Cumulative_Return':'Cumulative Return'})
        return fig_compare



