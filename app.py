# app.py (updated)
import streamlit as st
from data.fetch_data import fetch_indicator
from utils.indicators import INDICATORS, COUNTRIES
from visualizations.plot_utils import multi_country_chart

st.set_page_config("MacroView – Global Macro Dashboard", layout="wide")
st.title("🌐 MacroView – Global Macro Dashboard")

selected_countries = st.multiselect("🌍 Select Countries", list(COUNTRIES.keys()), default=["United States", "India"])
indicator = st.selectbox("📈 Select Economic Indicator", list(INDICATORS.keys()))

dfs = []
for country in selected_countries:
    df = fetch_indicator(COUNTRIES[country], INDICATORS[indicator])
    df["Country"] = country
    dfs.append(df)

if not dfs or any(df.empty for df in dfs):
    st.warning("One or more countries have missing data for this indicator.")
else:
    from pandas import concat
    combined_df = concat(dfs)
    fig = multi_country_chart(combined_df, indicator)
    st.plotly_chart(fig, use_container_width=True)
