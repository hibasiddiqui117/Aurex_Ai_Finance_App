# stock_predictor.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
import ta
from config import Config

class StockPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def fetch_data(self, symbol, period='1y'):
        """Fetch historical data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            if df.empty:
                # Fallback to manual date range
                df = yf.download(symbol, start=Config.START_DATE, end=Config.END_DATE)       
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()   
    def add_technical_indicators(self, df):
        """Add technical indicators to the data"""
        if df.empty:
            return df           
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        # RSI
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()       
        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()       
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['BB_upper'] = bollinger.bollinger_hband()
        df['BB_lower'] = bollinger.bollinger_lband()       
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()        
        # Price changes
        df['Daily_Return'] = df['Close'].pct_change()
        df['Price_Change'] = df['Close'].diff()        
        return df.dropna()    
    def prepare_features(self, df, forecast_days=5):
        """Prepare features for prediction"""
        features = df[['Close', 'Volume', 'SMA_20', 'SMA_50', 'RSI', 
                      'MACD', 'MACD_signal', 'BB_upper', 'BB_lower']].copy()        
        # Create lag features
        for lag in range(1, 6):
            features[f'Close_lag_{lag}'] = features['Close'].shift(lag)        
        # Target: Future price (5 days ahead)
        features['Target'] = features['Close'].shift(-forecast_days)       
        return features.dropna()   
    def train_model(self, features):
        """Train the prediction model"""
        X = features.drop(['Target'], axis=1)
        y = features['Target']       
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        predictions = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, predictions)
        
        return {
            'mae': mae,
            'last_training_date': datetime.now().strftime('%Y-%m-%d'),
            'features_used': list(X.columns)
        }
    
    def predict(self, symbol, days_ahead=5):
        """Make predictions for a given stock"""
        # Fetch and prepare data
        df = self.fetch_data(symbol)
        if df.empty:
            return None
            
        df = self.add_technical_indicators(df)
        features = self.prepare_features(df, days_ahead)
        
        if len(features) < 100:  # Need sufficient data
            return None
        
        # Train model
        training_info = self.train_model(features)
        
        # Prepare latest data for prediction
        latest_features = features.drop(['Target'], axis=1).iloc[-1:].copy()
        latest_scaled = self.scaler.transform(latest_features)
        
        # Make prediction
        prediction = self.model.predict(latest_scaled)[0]
        current_price = df['Close'].iloc[-1]
        
        return {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'predicted_price': round(prediction, 2),
            'prediction_date': (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d'),
            'days_ahead': days_ahead,
            'price_change_pct': round(((prediction - current_price) / current_price) * 100, 2),
            'training_info': training_info,
            'confidence': max(0, min(100, 100 - training_info['mae']))
        }