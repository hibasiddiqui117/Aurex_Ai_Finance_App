# data_fetcher.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self):
        self.sp500_symbols = self._load_sp500_symbols()
    
    def _load_sp500_symbols(self):
        # Top S&P 500 stocks
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 
                'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'HD', 'BAC']
    
    def fetch_data(self, symbol, period='1y', interval='1d'):
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period, interval=interval)
            
            # Calculate technical indicators
            df['MA_20'] = df['Close'].rolling(window=20).mean()
            df['MA_50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = self._calculate_rsi(df['Close'])
            
            return df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def _calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_available_symbols(self):
        return self.sp500_symbols