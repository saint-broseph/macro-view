import streamlit as st
import pandas as pd
from data.fetch_data import fetch_indicator
from data.countries import get_all_countries
from utils.indicators import INDICATORS
from visualizations.plot_utils import multi_country_chart
from data.realtime_data import fetch_realtime_etf_data, ETF_SYMBOLS
from utils.snapshots_indicators import SNAPSHOT_INDICATORS
import plotly.express as px

# Page config
st.set_page_config(page_title="🌐 MacroView", layout="wide")
st.title("🌐 MacroView – Global Macro Dashboard")

# Load all available countries dynamically
all_countries = get_all_countries()

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Macro Dashboard",
    "⚡ Real-Time Dashboard",
    "📄 Country Snapshot",
    "🆚 Country Comparison"
])

# ===============================
# 🌍 TAB 1 — Macro Dashboard
# ===============================
with tab1:
    st.sidebar.header("🛠 Configuration")

    selected_countries = st.sidebar.multiselect(
        "🌍 Select Countries",
        options=list(all_countries.keys()),
        default=[]
    )

    selected_indicator = st.sidebar.selectbox(
        "📈 Select Economic Indicator",
        options=list(INDICATORS.keys())
    )

    if not selected_countries:
        st.warning("⚠️ Please select at least one country.")
    else:
        dfs = []
        for country in selected_countries:
            country_code = all_countries.get(country)
            indicator_code = INDICATORS.get(selected_indicator)
            if country_code and indicator_code:
                df = fetch_indicator(country_code, indicator_code)
                if not df.empty:
                    df["Country"] = country
                    dfs.append(df)

        if not dfs:
            st.warning("⚠️ No available data for the selected indicator and countries.")
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
# 📄 TAB 3 — Country Snapshot
# ===============================
with tab3:
    st.subheader("📄 Country Snapshot Dashboard")
    selected_country = st.selectbox("Select a country", options=list(all_countries.keys()))

    col1, col2 = st.columns(2)
    for idx, indicator in enumerate(SNAPSHOT_INDICATORS):
        country_code = all_countries.get(selected_country)
        indicator_code = INDICATORS.get(indicator)
        if country_code and indicator_code:
            df = fetch_indicator(country_code, indicator_code)
            if not df.empty:
                latest_year = df["Year"].max()
                latest_value = df[df["Year"] == latest_year]["Value"].values[0]
                with (col1 if idx % 2 == 0 else col2):
                    st.metric(label=indicator, value=f"{latest_value:,.2f}", delta=f"Year: {latest_year}")

# ===============================
# 🆚 TAB 4 — Country Comparison
# ===============================
with tab4:
    st.subheader("🆚 Country Comparison Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        country1 = st.selectbox("Country 1", list(all_countries.keys()))
    with col2:
        country2 = st.selectbox("Country 2", list(all_countries.keys()))

    col1, col2 = st.columns(2)
    for idx, indicator in enumerate(SNAPSHOT_INDICATORS):
        code1 = all_countries.get(country1)
        code2 = all_countries.get(country2)
        indicator_code = INDICATORS.get(indicator)
        if code1 and code2 and indicator_code:
            df1 = fetch_indicator(code1, indicator_code)
            df2 = fetch_indicator(code2, indicator_code)

            if not df1.empty and not df2.empty:
                latest1 = df1[df1["Year"] == df1["Year"].max()]["Value"].values[0]
                latest2 = df2[df2["Year"] == df2["Year"].max()]["Value"].values[0]

                with (col1 if idx % 2 == 0 else col2):
                    st.metric(
                        label=indicator,
                        value=f"{country1}: {latest1:,.2f}",
                        delta=f"{country2}: {latest2:,.2f}"
                    )
