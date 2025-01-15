import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns
from datetime import datetime,timedelta
import yfinance as yf
from streamlit import session_state, container
from streamlit_autorefresh import st_autorefresh
import time
import Function
import socket



import numpy as np
import os







lists_stocks = {'Magnificent_Seven':['GOOG','AMZN','AAPL','META','MSFT','NVDA','TSLA']
                 ,'TA_IND':['TA35.TA','TA90.TA','^TA125.TA'],
                  'Global_ind':['SPY','QQQ','^RUT','^DJI','^N225']}
#Define tabs 1 ,2 to insert tiker and range dates

col_sym,col_update = st.columns([2,1.7])
with col_sym:


    tiker = st.text_input("Symbol",placeholder= "For example: AAPL")
    tiker = tiker.upper()
    if tiker:
            info_stock = yf.Ticker(tiker)
            tiker_check= Function.check_valid_tiker(info_stock)


    expander_sp = st.sidebar.expander("S&P 500 companies", expanded=False)
    expander_nas = st.sidebar.expander("NASDAQ 100 companies", expanded=False)
    expander_search = st.sidebar.expander("Search history", expanded=False)
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
    with expander_search:
        search_df = Function.get_history_search()
        st.dataframe(search_df)
    if tiker:
        if tiker_check == 'Valid':
            Function.create_log(tiker)
            real_tiker = Function.real_data(info_stock)

            col1,col2,col3 =  st.columns(3)
            with col1:
                st.markdown(f"##### {real_tiker[0]}")
            with col2:
                st.markdown(f"##### {round(real_tiker[1],2)}")
            with col3:
                formatted_value = Function.format_value_chg(real_tiker[-1])
                st.markdown(f"##### {formatted_value}", unsafe_allow_html=True)
            fig = Function.candle_stick(info_stock)
            st.plotly_chart(fig)


with col_update:
    if 'last_choice' not in st.session_state:
        st.session_state.last_choice = "Magnificent_Seven"
    left_si, mid, right_si = st.columns([2, 1.5, 1.5])
    if left_si.button("Magnificent 7"):
        st.session_state.last_choice = "Magnificent_Seven"

    if mid.button("Israel Indexes"):
        st.session_state.last_choice = "TA_IND"


    if right_si.button("Global Indexes"):
        st.session_state.last_choice = "Global_ind"

    placeholder = st.empty()

# Set the refresh interval
    refresh_interval_ms = 60 * 1000 * 5


    # container = st.container()
    with placeholder.container():

        if st.session_state.last_choice:
            choice = st.session_state.last_choice
            Function.real_list(lists_stocks[choice])
        current_time = time.localtime()
        current_seconds = time.mktime(current_time)
        new_seconds = current_seconds + 5 * 60
        new_time = time.localtime(new_seconds)
        st.write(f"Last refreshed at: {time.strftime('%H:%M:%S')} the next update at: {time.strftime("%H:%M:%S", new_time)}")

        st_autorefresh(interval=refresh_interval_ms, key="dynamic_refresh")



if tiker:
    if tiker_check=='Valid':

        col1,col2,col3 =st.columns(3)
        with col1:
            df_meta = Function.meta_fund_data(info_stock)[0]
            st.markdown(df_meta.to_html(header=False),unsafe_allow_html=True)
        with col2:
            df_ratios = Function.ratios_grow(info_stock)[0]
            df_ratios = df_ratios.set_index('multiplier')
            df_ratios.index.name = None
            st.markdown(df_ratios.to_html(header=False),unsafe_allow_html=True)
        with col3:
            growth = Function.ratios_grow(info_stock)[1]
            growth = growth.set_index('growth')
            growth.index.name = None
            st.markdown(growth.to_html(header=False),unsafe_allow_html=True)

        # expander_mean = st.expander("Average Ratios and Cagr sector",expanded=False)

        mean_sector = st.button("Average Ratios and Cagr of sector")
        if mean_sector:
            with st.expander("Average Ratios and Cagr of sector"):
                sector = df_meta.loc['sector'].max()
                st.markdown(f"#### {sector}")
                st.write("The average calculated by 50 big market cap. in sector")

                symbols_sector = Function.get_company_sector(sector.lower(),50)[1]
                if symbols_sector is not None:
                    concat_multi,concat_growth,mean_ratios,mean_growths = Function.compare_tiker_sector(symbols_sector)
                    col_ratio,col_growth = st.columns(2)
                    with col_ratio:
                        st.dataframe(mean_ratios)
                    with col_growth:
                        st.dataframe(mean_growths)
                    st.write("*Stocks with a change from positive EPS to negative or vice versa were excluded from the average.")

        today = datetime.now()
        week_before = today + timedelta(weeks=-1)
        st.experimental_fragment("history_analysis")
        sector = df_meta.loc['sector'].max().lower()
        d = st.container()
        with d:
            range_date = st.date_input(
                    "Range of dates"
                    " (by default is one week back from today)",
                    (week_before,today),
                    format="YYYY-MM-DD",
                    max_value=today
            )
            try:
                list_dates = [datetime.strftime(d, '%Y-%m-%d') for d in range_date]
                df_history =  Function.create_history_df_yf(info_stock,list_dates[0],list_dates[1])
            except:
                df_history = None


            if df_history is not None:
                # list_dates = [datetime.strftime(d,'%Y-%m-%d') for d in range_date]
                st.write(f"""
                The range date for history data is : from {' to '.join(list_dates)}
                """)
                df_history =  Function.create_history_df_yf(info_stock,list_dates[0],list_dates[1])
                if df_history is not None:
                    st.dataframe(df_history[['Open','High','Low','Close','Volume']])

                    st.markdown("---")
                    with st.expander("Analysis Graphs and compare to indexes"):
                        col_com,col_graph = st.columns([1,4])
                        with col_com:
                            input_index = st.selectbox(label='Index to compare',
                                                       options=[None, 'SPY - S&P 500', 'QQQ - NASDAQ',
                                                                "^RUT - russell 2000"],
                                                       placeholder="Choose index to compare")
                            if input_index:
                                index_sym = input_index.split("-")[0][:-1]
                                info_stock_index = yf.Ticker(index_sym)
                                history_index = Function.create_history_df_yf(info_stock_index, start=list_dates[0],
                                                                              end=list_dates[1])
                            else:
                                history_index = None


                            with col_graph:
                                tab_line,tab_Cumulative, tab_box = st.tabs(['Close price Over Time','Cumulative Returns','Box plot for years'])

                                with tab_line:
                                    fig_line = Function.create_plot_index(tiker,df_history,history_index,'close')

                                    st.plotly_chart(fig_line)

                                with tab_Cumulative:

                                    fig_compare = Function.create_plot_index(tiker, df_history,history_index,'Cumulative')

                                    st.plotly_chart(fig_compare)

                                with tab_box:
                                    fig_box_day,fig_box_month = Function.create_plot_index(tiker,df_history,history_index,'box')


                                    st.plotly_chart(fig_box_day)
                                    diff_days = (datetime.strptime(list_dates[1], '%Y-%m-%d') - datetime.strptime(list_dates[0],
                                                                                                                  '%Y-%m-%d')).days
                                    if diff_days>=30:
                                        st.markdown("---")
                                        st.plotly_chart(fig_box_month)
                    if "compression_sector" not in st.session_state:
                        st.session_state.compression_sector = False
                    if "top_n" not in st.session_state:
                        st.session_state.top_n = 1
                    try:
                        with st.expander("Comparison to the sector"):

                            compression_sector = st.button("Comparison with companies in the sector")

                            if compression_sector:

                                st.session_state.compression_sector = not st.session_state.compression_sector
                            if st.session_state.compression_sector:
                                top_n = st.selectbox(label="Number of top companies to compare",options=range(1,11))

                                if top_n:

                                        st.session_state.top_n = top_n

                                        # st.write(st.session_state['top_n'])
                                        sector_history_df = Function.df_sector_union(tiker, sector, st.session_state['top_n'],start = list_dates[0],end = list_dates[1])


                                        col_interval, col_graph_sector = st.columns([1, 4])
                                        with col_interval:
                                            dict_graph = {"Day":"Date","Month":"YearMonth","Year":"Year"}
                                            input_interval = st.selectbox(label='Interval display',
                                                                       options=['Day','Month','Year'])
                                        with col_graph_sector:
                                            tab_price,tab_return, tab_Cumulative, tab_box = st.tabs(['Price','Return','Cumulative Returns','Box Plot'])
                                            with tab_price:
                                                fig_close = Function.plots_sector(sector_history_df, dict_graph[input_interval],
                                                                                  "close")
                                                st.plotly_chart(fig_close)

                                            with tab_return:
                                                fig_return = Function.plots_sector(sector_history_df,dict_graph[input_interval],"return")
                                                st.plotly_chart(fig_return)

                                            with tab_Cumulative:
                                                fig_Cumulative = Function.plots_sector(sector_history_df,dict_graph[input_interval],"line_Cumulative")
                                                st.plotly_chart(fig_Cumulative)

                                            with tab_box:
                                               fig_box = Function.plots_sector(sector_history_df,dict_graph[input_interval],"box")
                                               st.plotly_chart(fig_box)



                    except ValueError as e:
                     if "One of ms" in str(e):
                         st.warning("Not have data about sector")

        # if st.button("Advanced Graphs"):
        #     AV = AutoViz_Class()
        #     st.write("AutoViz EDA Analysis:")
        #     AV = AV.AutoViz(filename='', dfte=df_history)
            # os.remove("temp_sweetviz_report.html")










