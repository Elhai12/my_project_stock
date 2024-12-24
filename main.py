import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns
from datetime import datetime,timedelta

key_code = st.secrets['my_secret_key']
st.markdown("""
#                *This is my first app*

""")
st.write("## Please choose symbol and range of dates")
tab1,tab2 = st.tabs(['Symbol','Dates'])
with tab1:
    tikker = st.text_input("The symbol",placeholder= "Insert here the symbol, for example: AAPL")

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
if tikker !='':
    tikker = tikker
else:
    tikker = "Not chosen yet"
st.write(f"""
The symbol was chosen is : {tikker}
\nThe range date for data is : from {' to '.join([datetime.strftime(d,'%Y-%m-%d') for d in range_date])}

""")
