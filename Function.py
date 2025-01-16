import plotly as plt
import pandas as pd
import requests
import pytz
import yfinance as yf
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from yahooquery import Screener
import sqlite3
import streamlit.components.v1 as components


def from_utc_israel(utc_time):
    utc = pytz.utc
    israel = pytz.timezone('Asia/Jerusalem')
    utc_time_local = utc.localize(utc_time)
    local_time = utc_time_local.astimezone(israel)
    return local_time

def check_valid_tiker(info_stock):

    try:
        sym = info_stock.info['shortName']
        tiker_check_test = 'Valid'
        return tiker_check_test
    except Exception as er:
        if str(er) == "'shortName'":
            st.warning("The symbol not valid")
            tiker_check_test = 'Invalid'
        else:
            st.warning(f"Error: {er}")
            tiker_check_test = 'Valid'
        return tiker_check_test


def meta_fund_data(info_stock):
    info_stock = info_stock.info
    metadata_cols = [
        "shortName", "currency", "sector","industry", "country"]

    fundamentals_cols = [
        "marketCap", "enterpriseValue", "trailingPE", "forwardPE","bookValue",
        "ebitda", "totalRevenue","revenuePerShare", "freeCashflow", "operatingCashflow",
        "currentRatio", "quickRatio", "debtToEquity"]

    df_fundamentals = pd.DataFrame.from_dict(info_stock, orient='index').T[fundamentals_cols].reset_index(drop=True).map(lambda x: round(x, 2))
    df_meta_data = pd.DataFrame.from_dict(info_stock,orient='index')

    df_meta_data = df_meta_data[df_meta_data.index.isin(metadata_cols)]

    # df_meta_data.columns = ['Metadata Field', 'Value']
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

    company_name = info_stock.info['shortName']
    df_day = info_stock.history(period='1d',interval='1m')
    last_price = df_day['Close'].iloc[-1]
    last_time = df_day.index[-1]
    previous_price = info_stock.info['previousClose']
    chg_day = ((last_price/previous_price)-1) *100
    list_real_data = [company_name,last_price,previous_price,chg_day]

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
        dict_stocks[tiker] = [list_real[1],format_value_chg(list_real[3])]


    items_list = list(dict_stocks.items())
    if len(items_list) %2 != 0:
        items_list.append((None,None))
    pairs_stocks = [(items_list[i],items_list[i+1]) for i in range(0,len(items_list),2)]
    # st.write(pairs_stocks)
    continer_1 = st.container(border=True)
    continer_2 = st.container(border=True)
    for tiker in pairs_stocks:

        col_1,col_2,divider,col_3,col_4 = st.columns([1,1,0.05,1,1])
        with st.container(border=True):
            with col_1:
                st.write(tiker[0][0])
                st.markdown(f"###### {round(tiker[0][1][0],2)}")
            with col_2:
                st.markdown(f"{tiker[0][1][1]}", unsafe_allow_html=True)
            if tiker[1][0] == None:
                continue
        with divider:
            st.write("|")

        with st.container(border =True):
            with col_3:
                st.write(tiker[1][0])
                st.markdown(f"###### {round(tiker[1][1][0],2)}")
            with col_4:
                st.markdown(f"{tiker[1][1][1]}", unsafe_allow_html=True)


    return




def create_history_df_yf(info_stock,start,end):

    tiker = info_stock.info['symbol']
    df_history = info_stock.history(start=start, end=end, interval='1d')
    df_history = df_history.reindex(pd.date_range(start=df_history.index.min(), end=df_history.index.max(), freq='D'))
    df_history['Close'] = df_history['Close'].ffill()
    df_history['Date'] = pd.to_datetime(df_history.index)

    df_history['year'] = df_history['Date'].dt.year

    df_history[['Open','High','Low','Close','Volume']] = df_history[['Open','High','Low','Close','Volume']].ffill()
    df_history['Daily_change_percent'] = (df_history['Close'].pct_change())*100
    df_history['chg_month'] = (df_history['Close'].pct_change(periods=30))*100
    df_history['symbol'] = tiker
    df_history['Cumulative_Return'] = ((1 + (df_history['Daily_change_percent']/100)).cumprod() - 1)*100
    df_history.index = pd.to_datetime(df_history.index).date


    return df_history



def create_plot_index(tiker,history_df,index_df,type_plot):
    color_ind = None
    add_title = ''

    if index_df is not None:
        color_ind = 'symbol'
        index_sym = index_df.symbol.max()
        add_title = f'vs {index_sym}'
        df_fill_index =index_df
        df_concat = pd.concat([history_df, df_fill_index], axis=0)

    else:
        df_concat = history_df

    if type_plot == 'box':
        fig_day = px.box(df_concat,x='year',y='Daily_change_percent',color = color_ind,title=f"Box plot for daily returns percent compare years for {tiker} {add_title}",
                         labels={'Daily_change_percent':'Daily Returns'})
        fig_day.update_layout(yaxis_ticksuffix='%')
        fig_month = px.box(df_concat,x='year',y='chg_month',color = color_ind,title=f"Box plot for monthly returns compare years for {tiker} {add_title}",
                           labels={'chg_month':'Monthly Returns'})
        fig_month.update_layout(yaxis_ticksuffix='%')
        return fig_day,fig_month


    elif type_plot == 'close':
        fig_line_close = px.line(df_concat, x="Date", y="Close",color = color_ind, title=f'Price close over time for {tiker} {add_title}',labels={"Close": "Close Price"})

        return fig_line_close

    elif type_plot == 'Cumulative':

        fig_compare = px.line(df_concat,x='Date',y='Cumulative_Return',color=color_ind,title=f'Cumulative Return {tiker} {add_title}'
                              ,labels={'Cumulative_Return':'Cumulative Return'})
        fig_compare.update_layout(yaxis_ticksuffix='%')
        return fig_compare


def candle_stick(stock_info):
    df = stock_info.history(period='1d', interval='1m')
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    return fig


def cagr_four(df):
    end_value = df.iloc[0]
    start_value = df.iloc[-1]
    if start_value < 0 or end_value < 0:
        cagr = None
    else:
        cagr = (((end_value/start_value) ** (1/4))-1) *100
    return cagr

def ratios_grow(stock_info):
    multipliers = {
        "Trailing P/E": stock_info.info.get("trailingPE"),
        "Forward P/E": stock_info.info.get("forwardPE"),
        "Price to Book (P/B)": stock_info.info.get("priceToBook"),
        "Price to Sales (P/S)": stock_info.info.get("priceToSalesTrailing12Months"),
        "EV/EBITDA": stock_info.info.get("enterpriseToEbitda"),
        "Dividend Yield": stock_info.info.get("dividendYield"),
    }
    income_statement = stock_info.income_stmt.T
    revenues = income_statement["Total Revenue"].iloc[-5:-1]
    net_incomes = income_statement["Net Income"].iloc[-5:-1]
    eps_history = income_statement["Basic EPS"].iloc[-4:]

    growth = {
        "Cagr Revenue AVG.4Y" : cagr_four(revenues),
        "Cager Income AVG.4Y" : cagr_four(net_incomes),
        "Cager EPS AVG.4Y": cagr_four(eps_history)

    }
    df_multi = pd.DataFrame(multipliers.items(),columns=['multiplier','value'])
    # df_multi["value"] = df_multi["value"].apply(lambda x: x.real if isinstance(x, complex) else x)
    df_multi['value'] = pd.to_numeric(df_multi["value"], errors="coerce")
    df_multi = df_multi.dropna(subset=["value"])
    df_multi['value'] = df_multi['value'].apply(lambda x: round(x,2))

    df_growth =pd.DataFrame(growth.items(),columns=['growth','value'])
    # df_growth["value"] = df_growth["value"].apply(lambda x: x.real if isinstance(x, complex) else x)
    df_growth['value'] = pd.to_numeric(df_growth["value"], errors="coerce")
    df_growth = df_growth.dropna(subset=["value"])
    df_growth['value'] = df_growth['value'].apply(lambda x: round(x, 2))

    return df_multi,df_growth

def get_company_sector(sector,count):
    try:
        s = Screener()
        data = s.get_screeners(f'ms_{sector}', count=count)
        dict_data = data[f'ms_{sector}']['quotes']
        df_symbols = pd.DataFrame.from_dict(dict_data)[['symbol','shortName','trailingPE','priceToBook','marketCap']]
        symbols = df_symbols.symbol.tolist()
        return df_symbols,symbols
    except ValueError as e:
        if "One of ms" in str(e):
            symbols = None
            st.warning("Not have data about the sector")
            return symbols,symbols

def compare_tiker_sector(symbols):

    concat_multi = None
    concat_growth = None
    stock_info_all = yf.Tickers(symbols)
    for symbol in symbols:
        stock_info = stock_info_all.tickers[symbol]
        df_multi,df_growth = ratios_grow(stock_info=stock_info)
        df_multi['symbol'] = symbol
        df_growth['symbol'] = symbol
        if concat_multi is None:
            concat_multi = df_multi
            concat_growth = df_growth

        else:
            concat_multi = pd.concat([concat_multi,df_multi],axis=0)
            concat_growth = pd.concat([concat_growth, df_growth], axis=0)

    df_mean_ratios = concat_multi.groupby('multiplier')['value'].mean()
    df_mean_ratios = df_mean_ratios.apply(lambda x:round(x,2))
    df_mean_growths = concat_growth.groupby('growth')['value'].mean()
    df_mean_growths = df_mean_growths.apply(lambda x: round(x, 2))
    return concat_multi,concat_growth,df_mean_ratios,df_mean_growths

def remove_table():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("delete from search_logs")
    conn.commit()
    conn.close()



def  create_log(symbol):

    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("insert into search_logs (symbol) values(?)",(symbol,))
    conn.commit()
    conn.close()

def get_history_search():
    conn = sqlite3.connect("stock.db")
    query = "select * from search_logs order by search_time DESC"
    df_search = pd.read_sql_query(query,conn)
    conn.close()
    return df_search

def df_sector_union(tiker,sector,count,start,end):
    symbols = get_company_sector(sector,count)[1]
    symbols.append(tiker)
    stock_info_all = yf.Tickers(symbols)
    data_sector = stock_info_all.history(start=start, end=end, interval='1d')['Close']
    data_sector = data_sector.reindex(pd.date_range(start=data_sector.index.min(), end=data_sector.index.max(), freq='D'))
    data_sector = data_sector.ffill()
    data_re = data_sector.reset_index()
    unpivot_data = data_re.melt(id_vars="index",var_name="Stock",value_name="Close")
    unpivot_data.rename(columns={"index": "Date_row"}, inplace=True)
    unpivot_data['rate_change'] = (unpivot_data['Close'].pct_change())*100
    unpivot_data['chg_month'] = (unpivot_data['Close'].pct_change(periods=30))*100
    # unpivot_data['chg_year'] = unpivot_data['Close'].pct_change(periods=365)
    unpivot_data['Cumulative_Return'] = ((1 + (unpivot_data['rate_change']/100)).cumprod() - 1)*100
    unpivot_data['Year'] = unpivot_data['Date_row'].dt.year
    unpivot_data['YearMonth'] = unpivot_data['Date_row'].dt.to_period('M').astype(str)
    unpivot_data['Date'] = unpivot_data['Date_row'].dt.date

    return unpivot_data
def agg_data(df,col_agg):
    df = df.sort_values("Date")
    df_agg = df.groupby([col_agg,'Stock'])['Close'].last().reset_index()
    df_agg['rate_change'] = (df_agg['Close'].pct_change())*100
    df_agg['Cumulative_Return'] = ((1 + (df_agg['rate_change']/100)).cumprod() - 1)*100
    return df_agg

def plots_sector(data_sector,month_year_day,type_plot):
    if (month_year_day != 'Date' and type_plot != 'box') or (type_plot == 'box' and month_year_day =='Year'):
        data_sector =  agg_data(data_sector,month_year_day)
    if type_plot == "close":
        fig = px.line(data_sector,x=month_year_day,y='Close',color='Stock',title=f'Price Compare'
                              ,labels={'Close':'Close Price'})

        return fig

    if type_plot == "return":
        fig = px.line(data_sector,x=month_year_day,y='rate_change',color='Stock',title=f'Return Compare'
                              ,labels={'rate_change':'Return'})
        fig.update_layout(yaxis_ticksuffix='%')
        return fig
    if type_plot == "line_Cumulative":
        fig = px.line(data_sector,x=month_year_day,y='Cumulative_Return',color='Stock',title=f'Cumulative Return Compare'
                              ,labels={'Cumulative_Return':'Cumulative Return'})
        fig.update_layout(yaxis_ticksuffix='%')
        return fig
    if type_plot == 'box':



        if month_year_day == 'Date':
            y_val = 'rate_change'
            label = 'Daily Change'
            fig = px.box(data_sector, x='Year', y='rate_change', color='Stock', title=f'Daily Return Distribution'
                         , labels={y_val: label})
        elif month_year_day == 'YearMonth':
            y_val = 'chg_month'
            label = 'Monthly Change'
            fig = px.box(data_sector, x='Year', y='chg_month', color='Stock', title=f'Monthly Return Distribution'
                         , labels={y_val: label})
        elif month_year_day == 'Year':

            fig = px.box(data_sector, x='Stock', y='rate_change', title=f'Yearly Return Distribution'
                         , labels={'rate_change': 'Yearly Change'})
        fig.update_layout(yaxis_ticksuffix='%')
        return fig






