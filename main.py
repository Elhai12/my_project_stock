import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns
from datetime import datetime,timedelta
import yfinance as yf
from streamlit import session_state
from streamlit_autorefresh import st_autorefresh
import time
import Function


#Define secret code
key_code = st.secrets['my_secret_key']


st.image("banner.jpg")


lists_stocks = {'Magnificent_Seven':['GOOG','AMZN','AAPL','META','MSFT','NVDA','TSLA']
                 ,'TA_IND':['TA35.TA','TA90.TA','^TA125.TA'],
                  'Global_ind':['SPY','QQQ','^RUT','^DJI','^N225']}
#Define tabs 1 ,2 to insert tiker and range dates

col_date_sym,col_update = st.columns([1,1])
with col_date_sym:
    today = datetime.now()
    week_before = today + timedelta(weeks=-1)
    range_date = st.date_input(
        "Range of dates"
        " (by default is one week back from today)",
        (week_before,today),
        format="YYYY-MM-DD",
        max_value=today
    )
# with col_symb:
    # col_tiker,col_df =st.columns([2,1.5])
    # with col_tiker:
    tiker = st.text_input("Symbol",placeholder= "For example: AAPL")
    tiker = tiker.upper()
    if tiker:
            info_stock = yf.Ticker(tiker)
            tiker_check= Function.check_valid_tiker(info_stock)
    expander_sp = st.expander("Show all companies in S&P 500", expanded=False)
    expander_nas = st.expander("Show all companies in NASDAQ 100", expanded=False)
    with expander_sp:
        df_sym_sp = pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        df_sym_sp = df_sym_sp.rename(columns={'Security':'Company'})[['Symbol', 'Company']]
        df_sym_sp.set_index('Company',inplace=True)
        st.dataframe(df_sym_sp)
    with expander_nas:
        comp_nasdaq = pd.read_html('https://en.m.wikipedia.org/wiki/Nasdaq-100')
        df_sym_nas = pd.DataFrame(comp_nasdaq[4])
        df_sym_nas = df_sym_nas[['Symbol', 'Company']]
        df_sym_nas.set_index('Company', inplace=True)
        st.dataframe(df_sym_nas)


with (col_update):
    if 'last_choice' not in st.session_state:
        st.session_state.last_choice = None
    left_si, mid, right_si = st.columns([2, 1.5, 1.5])
    if left_si.button("Magnificent 7"):
        st.session_state.last_choice = "Magnificent_Seven"

    if mid.button("Israel Indexes"):
        st.session_state.last_choice = "TA_IND"


    if right_si.button("Global Indexes"):
        st.session_state.last_choice = "Global_ind"

    placeholder = st.empty()

# Set the refresh interval
    refresh_interval_ms = 60 * 1000



    with placeholder.container():

        if st.session_state.last_choice:
            choice = st.session_state.last_choice
            Function.real_list(lists_stocks[choice])

        st.write(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

        st_autorefresh(interval=refresh_interval_ms, key="dynamic_refresh")

list_dates = [datetime.strftime(d,'%Y-%m-%d') for d in range_date]

#After the user press enter and the tiker variable inserted

#Check if tiker valid

#Define tab 4,5 for meta data and fundamental data from yfinance
if tiker:
    if tiker_check=='Valid':

        tab3,tab4 =st.tabs(['Metadata Symbol','Fundamental Data'])
        with tab3:
            df_meta = Function.meta_fund_data(info_stock)[0]
            st.dataframe(df_meta)
        with tab4:
            df_fund = Function.meta_fund_data(info_stock)[1]
            st.dataframe(df_fund)

#Present the current daily data using API

        st.markdown("---")
        # st.markdown("Current daily data")
        data_currently_list = Function.real_data(info_stock)

        if data_currently_list:
            last_price, previous_price, chg_day_org = data_currently_list
            with st.container():
                col1, col2, col3,col4 = st.columns(4)
                with col1:
                    st.metric(label="Symbol", value=tiker)
                with col2:
                    st.metric(label="last Price today", value=f"{float(last_price):.2f}")
                with col3:
                    st.metric(label=" The previous day price", value=f"{float(previous_price):.2f}")

                with col4:
                    formatted_value = Function.format_value_chg(chg_day_org)
                    st.markdown(f"##### Change \n{formatted_value}", unsafe_allow_html=True)
#Define tab 5,6 for historical data and graphs using yfinance library and plotly
        tab_history,tab_graph = st.tabs(['Historical Data', 'Graphs'])

        with tab_history:
                st.write(f"""
                The range date for history data is : from {' to '.join(list_dates)}
                """)
                df_history =  Function.create_history_df_yf(info_stock,list_dates[0],list_dates[1])
                if df_history is not None:
                    st.dataframe(df_history[['Open','High','Low','Close','Volume']])

#Using a custom function I created for generating graphs based on the requested type.
                    with tab_graph:
                        tab_line, tab_box,tab_compare = st.tabs(['Line Over Time','Box plot for years','Compare stock with index'])
                        with tab_line:
                            fig_line = Function.create_plot(tiker,df_history,'line')
                            st.plotly_chart(fig_line)
                        with tab_box:
                            fig_box_day,fig_box_month = Function.create_plot(tiker,df_history,'box')


                            st.plotly_chart(fig_box_day)
                            diff_days = (datetime.strptime(list_dates[1], '%Y-%m-%d') - datetime.strptime(list_dates[0],
                                                                                                          '%Y-%m-%d')).days
                            if diff_days>=30:
                                st.markdown("---")
                                st.plotly_chart(fig_box_month)
                        with tab_compare:
                            input_index = st.selectbox(label='Index to compare',options=['SPY - S&P 500','QQQ - NASDAQ',"^RUT - russell 2000"],placeholder="Choose index to compare")
                            if input_index:
                                index_sym = input_index.split("-")[0][:-1]
                                info_stock_index = yf.Ticker(index_sym)

                                history_index = Function.create_history_df_yf(info_stock_index, start=list_dates[0],end=list_dates[1])
                                fig_compare = Function.create_plot(tiker, df_history, 'compare',index_df=history_index)

                                st.plotly_chart(fig_compare)





