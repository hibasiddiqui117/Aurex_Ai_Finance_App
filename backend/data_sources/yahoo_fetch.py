# data_sources/yahoo_fetch.py
import yfinance as yf
import pandas as pd

def fetch_latest_data(ticker="^GSPC", days=60):
    data = yf.download(ticker, period=f"{days}d", interval="1d")
    data['Return'] = data['Close'].pct_change()
    data['Volatility'] = data['Return'].rolling(30).std()
    data = data.dropna()
    return data
