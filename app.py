# app.py
import streamlit as st
from data.fetch_data import fetch_indicator
from utils.indicators import INDICATORS, COUNTRIES
from visualizations.plot_utils import line_chart

st.set_page_config("MacroView – Global Economic Dashboard", layout="wide")
st.title("📊 Global Macro Dashboard")

country = st.selectbox("🌍 Select Country", list(COUNTRIES.keys()))
indicator = st.selectbox("📈 Select Economic Indicator", list(INDICATORS.keys()))

with st.spinner("Fetching data from World Bank..."):
    df = fetch_indicator(COUNTRIES[country], INDICATORS[indicator])

if df.empty:
    st.warning("No data found for this combination.")
else:
    fig = line_chart(df, f"{indicator} for {country}")
    st.plotly_chart(fig, use_container_width=True)
