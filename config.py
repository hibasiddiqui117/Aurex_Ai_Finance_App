# config.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class Config:
    # Time period for historical data
    START_DATE = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
    END_DATE = datetime.now().strftime('%Y-%m-%d')
    # Popular stock symbols
    POPULAR_STOCKS = {
        'S&P 500': '^GSPC',
        'Apple': 'AAPL',
        'Microsoft': 'MSFT',
        'Google': 'GOOGL',
        'Amazon': 'AMZN',
        'Tesla': 'TSLA',
        'NVIDIA': 'NVDA',
        'Meta': 'META',
        'Netflix': 'NFLX',
        'AMD': 'AMD',
        'Intel': 'INTC',
        'JPMorgan': 'JPM',
        'Visa': 'V',
        'Walmart': 'WMT',
        'Johnson & Johnson': 'JNJ'
    }  
    # Technical indicators to calculate
    INDICATORS = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'BB_upper', 'BB_lower']