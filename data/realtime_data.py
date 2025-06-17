import yfinance as yf
import pandas as pd

# Define macro proxy ETFs
ETF_SYMBOLS = {
    "Inflation (US)": "TIP",
    "Interest Rates (US)": "TLT",
    "Global Equities": "ACWI",
    "Volatility (VIX)": "VIXY",
    "USD Strength": "UUP"
}

def fetch_realtime_etf_data(symbol, period="6mo", interval="1d"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    df.reset_index(inplace=True)
    df["Symbol"] = symbol
    return df
