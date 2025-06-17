import streamlit as st
import pandas as pd
import plotly.express as px

from data.fetch_data import fetch_indicator
from data.realtime_data import fetch_realtime_etf_data, ETF_SYMBOLS
from utils.indicators import INDICATORS, COUNTRIES
from utils.snapshots_indicators import SNAPSHOT_INDICATORS
from visualizations.plot_utils import multi_country_chart

# Page Configuration
st.set_page_config(page_title="🌐 MacroView", layout="wide")
st.title("🌐 MacroView – Global Macro Dashboard")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Macro Dashboard",
    "⚡ Real-Time Dashboard",
    "📄 Country Snapshot",
    "🆚 Country Comparison"
])

# ========================================
# 🌍 TAB 1 — Macro Dashboard
# ========================================
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

# ========================================
# ⚡ TAB 2 — Real-Time Dashboard
# ========================================
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

# ========================================
# 📄 TAB 3 — Country Snapshot
# ========================================
with tab3:
    st.subheader("📄 Country Snapshot")

    selected_country = st.selectbox("🌐 Select Country", list(COUNTRIES.keys()))
    snapshot_dfs = []

    for indicator in SNAPSHOT_INDICATORS:
        df = fetch_indicator(COUNTRIES[selected_country], SNAPSHOT_INDICATORS[indicator])
        if not df.empty:
            latest_year = df["Year"].max()
            latest_value = df[df["Year"] == latest_year]["Value"].values[0]
            snapshot_dfs.append({
                "Indicator": indicator,
                "Year": latest_year,
                "Value": latest_value
            })

    if snapshot_dfs:
        snapshot_df = pd.DataFrame(snapshot_dfs)
        st.dataframe(snapshot_df, use_container_width=True)
    else:
        st.warning("No snapshot data available for selected country.")

# ========================================
# 🆚 TAB 4 — Country Comparison
# ========================================
with tab4:
    st.subheader("🆚 Country Comparison Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        country1 = st.selectbox("🇦🇱 Country 1", list(COUNTRIES.keys()), index=0)
    with col2:
        country2 = st.selectbox("🇧🇷 Country 2", list(COUNTRIES.keys()), index=1)

    selected_metrics = st.multiselect(
        "📊 Select Indicators to Compare",
        options=list(SNAPSHOT_INDICATORS.keys()),
        default=["GDP (Current US$)", "Inflation Rate (CPI)", "Unemployment Rate"]
    )

    for indicator in selected_metrics:
        col1, col2 = st.columns(2)

        with col1:
            df1 = fetch_indicator(COUNTRIES[country1], SNAPSHOT_INDICATORS[indicator])
            if not df1.empty:
                st.plotly_chart(
                    px.line(df1, x="Year", y="Value", title=f"{country1} – {indicator}", markers=True),
                    use_container_width=True
                )

        with col2:
            df2 = fetch_indicator(COUNTRIES[country2], SNAPSHOT_INDICATORS[indicator])
            if not df2.empty:
                st.plotly_chart(
                    px.line(df2, x="Year", y="Value", title=f"{country2} – {indicator}", markers=True),
                    use_container_width=True
                )
