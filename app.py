import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.fetch_data import fetch_indicator
from data.realtime_data import fetch_realtime_etf_data, ETF_SYMBOLS
from utils.indicators import INDICATORS, COUNTRIES
from utils.snapshots_indicators import SNAPSHOT_INDICATORS
from visualizations.plot_utils import multi_country_chart

# Page config
st.set_page_config(page_title="🌐 MacroView", layout="wide")
st.title("🌐 MacroView – Global Macro Dashboard")

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Macro Dashboard",
    "⚡ Real-Time Dashboard",
    "📋 Country Snapshot",
    "🆚 Country Comparison"
])

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

# ===============================
# 📋 TAB 3 — Country Snapshot
# ===============================
with tab3:
    st.subheader("📋 Country Snapshot")

    selected_country = st.selectbox("Select a country", options=list(COUNTRIES.keys()), index=0)

    snapshot_data = []

    for label, code in SNAPSHOT_INDICATORS.items():
        df = fetch_indicator(COUNTRIES[selected_country], code)
        if not df.empty:
            latest_row = df.sort_values("Year", ascending=False).iloc[0]
            snapshot_data.append({
                "Indicator": label,
                "Year": int(latest_row["Year"]),
                "Value": round(latest_row["Value"], 2)
            })

    if not snapshot_data:
        st.warning("No data available for this country.")
    else:
        snapshot_df = pd.DataFrame(snapshot_data)
        st.dataframe(snapshot_df, use_container_width=True)

        if st.checkbox("📈 Show Historical Trends"):
            for label, code in SNAPSHOT_INDICATORS.items():
                df = fetch_indicator(COUNTRIES[selected_country], code)
                if not df.empty:
                    fig = px.line(df, x="Year", y="Value", title=label, markers=True)
                    fig.update_layout(template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

# ===============================
# 🆚 TAB 4 — Country Comparison
# ===============================
with tab4:
    st.subheader("🆚 Country Comparison Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        country1 = st.selectbox("🇦🇱 Country 1", list(COUNTRIES.keys()), index=0)
    with col2:
        country2 = st.selectbox("🇧🇷 Country 2", list(COUNTRIES.keys()), index=1)

    data1, data2 = {}, {}

    for label, code in SNAPSHOT_INDICATORS.items():
        df1 = fetch_indicator(COUNTRIES[country1], code)
        df2 = fetch_indicator(COUNTRIES[country2], code)

        # Get most recent non-null value
        if not df1.empty:
            latest1 = df1.dropna().sort_values("Year", ascending=False).iloc[0]
            data1[label] = latest1["Value"]
        else:
            data1[label] = None

        if not df2.empty:
            latest2 = df2.dropna().sort_values("Year", ascending=False).iloc[0]
            data2[label] = latest2["Value"]
        else:
            data2[label] = None

    # --- Show Comparison Table ---
    comp_df = pd.DataFrame({
        "Indicator": list(SNAPSHOT_INDICATORS.keys()),
        country1: [round(data1[ind], 2) if data1[ind] is not None else "N/A" for ind in SNAPSHOT_INDICATORS],
        country2: [round(data2[ind], 2) if data2[ind] is not None else "N/A" for ind in SNAPSHOT_INDICATORS],
    })

    st.dataframe(comp_df, use_container_width=True)

    # --- Comparison Bar Chart ---
    if st.checkbox("📊 Show Bar Chart Comparison"):
        for indicator in SNAPSHOT_INDICATORS.keys():
            val1 = data1[indicator]
            val2 = data2[indicator]

            if val1 is not None and val2 is not None:
                fig = go.Figure(data=[
                    go.Bar(name=country1, x=[indicator], y=[val1]),
                    go.Bar(name=country2, x=[indicator], y=[val2])
                ])
                fig.update_layout(
                    barmode='group',
                    title=f"{indicator} Comparison",
                    yaxis_title=indicator,
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

