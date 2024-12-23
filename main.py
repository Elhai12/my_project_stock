import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns

st.markdown("""
#                *This is my first app*

""")
df = sns.load_dataset('diamonds')
fig,ax = plt.subplots()
sns.scatterplot(data=df,x="carat",y="price",ax=ax)
plt.title("Carat by price")
st.pyplot(fig)