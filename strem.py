import streamlit as st
import pandas as pd

df = pd.DataFrame({
    "Stock": ["AAPL", "GOOGL", "MSFT"],
    "Daily Price": [150, 2800, 300],
    "Volatility": [1.2, 1.8, 1.5],
    "Volume": [5000000, 3000000, 4000000]
})

st.write("### Stock Data Table")
st.dataframe(df)  # Interactive table
