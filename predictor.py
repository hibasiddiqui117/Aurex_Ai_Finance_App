# predictor.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class StockPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
    
    def prepare_features(self, df):
        # Create features
        features = pd.DataFrame()
        features['Close'] = df['Close']
        features['Volume'] = df['Volume']
        features['MA_20'] = df['MA_20']
        features['MA_50'] = df['MA_50']
        features['RSI'] = df['RSI']
        
        # Lag features
        for lag in [1, 2, 3, 5]:
            features[f'Close_Lag_{lag}'] = df['Close'].shift(lag)
        
        # Moving averages
        features['MA_5'] = df['Close'].rolling(window=5).mean()
        features['MA_10'] = df['Close'].rolling(window=10).mean()
        
        # Price change
        features['Price_Change'] = df['Close'].pct_change()
        
        # Drop NaN
        features = features.dropna()
        
        return features
    
    def train_predict(self, df, days_to_predict=7):
        try:
            # Prepare data
            features = self.prepare_features(df)
            
            # Create target (future prices)
            target = df['Close'].shift(-days_to_predict)
            target = target[features.index]
            
            # Split data
            split_idx = int(len(features) * 0.8)
            X_train = features.iloc[:split_idx]
            X_test = features.iloc[split_idx:]
            y_train = target.iloc[:split_idx]
            y_test = target.iloc[split_idx:]
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Predict
            predictions = self.model.predict(X_test_scaled)
            
            return {
                'predictions': predictions,
                'actual': y_test.values,
                'dates': df.index[split_idx+days_to_predict:],
                'model_score': self.model.score(X_test_scaled, y_test)
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return None