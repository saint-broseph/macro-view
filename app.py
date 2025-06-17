import streamlit as st
import pandas as pd
from data.fetch_data import fetch_indicator
from utils.indicators import INDICATORS, COUNTRIES
from visualizations.plot_utils import multi_country_chart
from data.realtime_data import fetch_realtime_etf_data, ETF_SYMBOLS
import plotly.express as px

# Page config
st.set_page_config(page_title="🌐 MacroView", layout="wide")
st.title("🌐 MacroView – Global Macro Dashboard")

# --- Tabs ---
tab1, tab2 = st.tabs(["🌍 Macro Dashboard", "⚡ Real-Time Dashboard"])

# ===============================
# 🌍 TAB 1 — Macro Dashboard
# ===============================
with tab1:
    st.sidebar.header("🛠 Configuration")

    selected_countries = st.sidebar.multiselect(
        "🌍 Select Countries",
        options=list(COUNTRIES.keys()),
        default=["United States", "India", "China"]
    )

    selected_indicator = st.sidebar.selectbox(
        "📈 Select Economic Indicator",
        options=list(INDICATORS.keys())
    )

    dfs = []
    for country in selected_countries:
        df = fetch_indicator(COUNTRIES[country], INDICATORS[selected_indicator])
        if not df.empty:
            df["Country"] = country
            dfs.append(df)

    if not dfs or any(df.empty for df in dfs):
        st.warning("⚠️ One or more selected countries have no available data for this indicator.")
    else:
        combined_df = pd.concat(dfs)
        years = combined_df["Year"].dropna().unique()
        min_year, max_year = int(min(years)), int(max(years))

        start_year = st.sidebar.slider(
            "📅 Start Year",
            min_value=min_year,
            max_value=max_year,
            value=min_year
        )

        filtered_df = combined_df[combined_df["Year"] >= start_year]
        fig = multi_country_chart(filtered_df, selected_indicator)
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# ⚡ TAB 2 — Real-Time Dashboard
# ===============================
with tab2:
    st.subheader("⚡ Real-Time Economic Indicator Proxies (via ETFs)")
    selected_etfs = st.multiselect(
        "📊 Select Indicators",
        options=list(ETF_SYMBOLS.keys()),
        default=["Inflation (US)", "Interest Rates (US)", "Global Equities"]
    )

    etf_dfs = []
    for label in selected_etfs:
        df = fetch_realtime_etf_data(ETF_SYMBOLS[label])
        if not df.empty:
            df["Label"] = label
            etf_dfs.append(df)

    if not etf_dfs:
        st.warning("⚠️ No data available.")
    else:
        realtime_df = pd.concat(etf_dfs)
        fig = px.line(
            realtime_df,
            x="Date",
            y="Close",
            color="Label",
            title="Real-Time Indicator Trends (Last 6 Months)",
            markers=True
        )
        fig.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="ETF Price")
        st.plotly_chart(fig, use_container_width=True)
