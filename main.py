import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns
from datetime import datetime,timedelta
import Function

key_code = st.secrets['my_secret_key']
st.markdown("""
#                *App for data stock*

""")
st.write("#### Please choose symbol and range of dates")
tab1,tab2 = st.tabs(['Symbol','Dates'])
with tab1:
    tiker = st.text_input("The symbol",placeholder= "Insert here the symbol, for example: AAPL")

with tab2:
    today = datetime.now()
    week_before = today + timedelta(weeks=-1)
    range_date = st.date_input(
        "Choose the range of dates"
        " (by default is one week back from today)",
        (week_before,today),
        format="YYYY-MM-DD",
        max_value=today
    )
list_dates = [datetime.strftime(d,'%Y-%m-%d') for d in range_date]



if tiker !='':

    tiker = tiker
    st.write(f"""
    The symbol was chosen is : {tiker}
    \nThe range date for history data is : from {' to '.join(list_dates)}
    """)
    last_price, previous_price, chg_day = Function.data_today(tiker,key_code)
    st.markdown(f"## The last price today: {last_price}")
    st.markdown(f"## The previous day price: {previous_price}")
    if chg_day.startswith("-"):
        formatted_value = f'<span style="color:red;">&#x2193; {chg_day}</span>'
    else:
        formatted_value = f'<span style="color:green;">&#x2191; {chg_day}</span>'
    st.markdown(f"## The change percentage: {formatted_value}", unsafe_allow_html=True)

    tab3, tab4 = st.tabs(['Historical_data', 'Graphs'])
    with tab3:
        df_history =  Function.get_historical_data(tiker,list_dates[0],list_dates[1],key_code)
        st.dataframe(df_history)


else:
    st.write("Not chosen symbol yet")

