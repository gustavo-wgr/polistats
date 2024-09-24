import streamlit as st
import pandas as pd

# Sample data
data = pd.DataFrame({
        'Metric': ['GDP Growth', 'Unemployment Rate', 'Inflation Rate'],
        'Value': [2.3, 5.0, 1.6]
    })
def load_obama_data():
    return data

st.dataframe(data)
