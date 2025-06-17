import streamlit as st
import pandas as pd
from data.fetch_data import fetch_indicator
from utils.indicators import INDICATORS, COUNTRIES
from visualizations.plot_utils import multi_country_chart

# Page config
st.set_page_config(page_title="🌐 MacroView – Global Macro Dashboard", layout="wide")
st.title("🌐 MacroView – Global Macro Dashboard")

# --- Sidebar Inputs ---
st.sidebar.header("🛠 Configuration")

# Country selection
selected_countries = st.sidebar.multiselect(
    "🌍 Select Countries",
    options=list(COUNTRIES.keys()),
    default=["United States", "India", "China"]
)

# Indicator selection
selected_indicator = st.sidebar.selectbox(
    "📈 Select Economic Indicator",
    options=list(INDICATORS.keys())
)

# --- Fetch Data ---
dfs = []
for country in selected_countries:
    df = fetch_indicator(COUNTRIES[country], INDICATORS[selected_indicator])
    if not df.empty:
        df["Country"] = country
        dfs.append(df)

# --- Plot ---
if not dfs or any(df.empty for df in dfs):
    st.warning("⚠️ One or more selected countries have no available data for this indicator.")
else:
    combined_df = pd.concat(dfs)

    # --- Time Range Filter ---
    years = combined_df["Year"].dropna().unique()
    min_year, max_year = int(min(years)), int(max(years))

    start_year = st.sidebar.slider(
        "📅 Start Year",
        min_value=min_year,
        max_value=max_year,
        value=min_year,
        step=1
    )

    filtered_df = combined_df[combined_df["Year"] >= start_year]
    fig = multi_country_chart(filtered_df, selected_indicator)
    st.plotly_chart(fig, use_container_width=True)
