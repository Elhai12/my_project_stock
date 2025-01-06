import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns
from datetime import datetime,timedelta
import Function

#Define secret code
key_code = st.secrets['my_secret_key']
col1,col_title,col3 = st.columns([1,5,1])
with col_title:
    st.markdown("""# *Stock Market Information*""")

st.write("#### Please choose range of dates and symbol")
#Define tabs 1 ,2 to insert tiker and range dates
tab_date,tab_symb = st.tabs(['Dates','Symbol'])
with tab_date:
    today = datetime.now()
    week_before = today + timedelta(weeks=-1)
    range_date = st.date_input(
        "Choose the range of dates"
        " (by default is one week back from today)",
        (week_before,today),
        format="YYYY-MM-DD",
        max_value=today
    )
with tab_symb:
    col_tiker,col_df =st.columns([2,1.5])
    with col_tiker:
        tiker = st.text_input("The symbol",placeholder= "Insert here the symbol, for example: AAPL")
    with col_df:
        st.write("Table with all companies in S&P 500")
        tickers_df = pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        st.dataframe(tickers_df.sort_values('Symbol').iloc[:, :2])


list_dates = [datetime.strftime(d,'%Y-%m-%d') for d in range_date]

#After the user press enter and the tiker variable inserted
if tiker:
#Check if tiker valid
    tiker_check,info_stock = Function.check_valid_tiker(tiker)
#Define tab 4,5 for meta data and fundamental data from yfinance
    if tiker_check=='Valid':
        tab3,tab4 =st.tabs(['Metadata Symbol','Fundamental Data'])
        with tab3:
            df_meta = Function.meta_fund_data(info_stock)[0]
            st.dataframe(df_meta)
        with tab4:
            df_fund = Function.meta_fund_data(info_stock)[1]
            st.dataframe(df_fund)

#Present the current daily data using API
        tiker = tiker.upper()
        st.markdown("---")
        st.markdown("Current daily data")
        data_currently_list = Function.data_today(tiker, key_code)

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
                    chg_day = chg_day_org[:5]+"%"
                    if chg_day.startswith("-"):
                        formatted_value = f'<span style="color:red;">&#x2193; {chg_day}</span>'
                    else:
                        formatted_value = f'<span style="color:green;">&#x2191; {chg_day}</span>'
                    st.markdown(f"##### The change percentage \n{formatted_value}", unsafe_allow_html=True)
#Define tab 5,6 for historical data and graphs using yfinance library and plotly
        tab_history,tab_graph = st.tabs(['Historical Data', 'Graphs'])

        with tab_history:
                st.write(f"""
                The range date for history data is : from {' to '.join(list_dates)}
                """)
                df_history =  Function.create_history_df_yf(tiker,list_dates[0],list_dates[1])
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
                            input_index = st.selectbox(label='Index to compare',options=['SPY - S&P 500','QQQ - NASDAQ',"RUT - russell 2000"],placeholder="Choose index to compare")
                            if input_index:
                                index_sym = input_index.split("-")[0][:-1]

                                history_index = Function.create_history_df_yf(tiker=index_sym, start=list_dates[0],end=list_dates[1])
                                fig_compare = Function.create_plot(tiker, df_history, 'compare',index_df=history_index)

                                st.plotly_chart(fig_compare)




