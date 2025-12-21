import pandas as pd
import joblib

# Load model
model = joblib.load("market_model.pkl")

# Load data for prediction (latest rows)
df = pd.read_csv("cleaned_sp500_features.csv", index_col=0, parse_dates=True)

# Example: last 5 rows
X_new = df[['Return', 'Volatility']].tail()
preds = model.predict(X_new)

print(preds)  # 1 = up, 0 = down
