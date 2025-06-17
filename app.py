import streamlit as st
import pandas as pd
from data.fetch_data import fetch_indicator
from utils.indicators import INDICATORS, COUNTRIES
from visualizations.plot_utils import multi_country_chart

# Streamlit App Config
st.set_page_config(page_title="🌐 MacroView – Global Macro Dashboard", layout="wide")
st.title("🌐 MacroView – Global Macro Dashboard")

# Sidebar for User Input
st.sidebar.header("Configuration")
selected_countries = st.sidebar.multiselect(
    "🌍 Select Countries",
    options=list(COUNTRIES.keys()),
    default=["United States", "India", "China"]
)

selected_indicator = st.sidebar.selectbox(
    "📈 Select Economic Indicator",
    options=list(INDICATORS.keys()),
    index=0
)

# Fetch and Combine Data
dfs = []
for country in selected_countries:
    df = fetch_indicator(COUNTRIES[country], INDICATORS[selected_indicator])
    if not df.empty:
        df["Country"] = country
        dfs.append(df)

# Render Chart
if not dfs or any(df.empty for df in dfs):
    st.warning("⚠️ One or more selected countries have no available data for this indicator.")
else:
    combined_df = pd.concat(dfs)
    fig = multi_country_chart(combined_df, selected_indicator)
    st.plotly_chart(fig, use_container_width=True)
