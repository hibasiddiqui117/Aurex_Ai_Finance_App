# backend/app.py
from flask import Flask, jsonify
import pandas as pd
import yfinance as yf
import joblib
from bot.finance_bot import analyze_stock

app = Flask(__name__)

# Load trained model once
MODEL_PATH = "backend/models/market_model.pkl"
model = joblib.load(MODEL_PATH)

# --------- Utility Functions ---------
def fetch_latest_data(ticker="^GSPC", days=60):
    """
    Fetch latest market data from Yahoo Finance
    """
    data = yf.download(ticker, period=f"{days}d", interval="1d")
    data['Return'] = data['Close'].pct_change()
    data['Volatility'] = data['Return'].rolling(30).std()
    data = data.dropna()
    return data

def predict_market(data):
    """
    Predict market up/down based on last row
    """
    X_new = data[['Return', 'Volatility']].tail(1)
    pred = model.predict(X_new)[0]
    prob = model.predict_proba(X_new)[0]
    verdict = "UP 📈" if pred == 1 else "DOWN 📉"
    confidence = f"UP: {prob[1]:.2f}, DOWN: {prob[0]:.2f}"
    return verdict, confidence

# --------- Routes ---------
@app.route("/")
def home():
    return "Welcome to Aurex Finance AI Backend! Use /market_prediction or /analyze_stock."

@app.route("/market_prediction")
def market_prediction():
    data = fetch_latest_data("^GSPC")
    verdict, confidence = predict_market(data)
    return jsonify({"prediction": verdict, "confidence": confidence})

@app.route("/analyze_stock")
def analyze():
    # Example static input; later replace with real stock data
    financials = {
        "revenue_growth": 0.12,
        "profit_consistency": 0.9,
        "debt_level": 0.3,
        "promoter_holding_trend": 0.05,
        "valuation": "undervalued",
        "key_risks": "low",
        "business_model": "clear"
    }
    verdict, reasoning = analyze_stock(financials)
    return jsonify({"verdict": verdict, "reasoning": reasoning})

@app.route("/predict_stock/<ticker>")
def predict_stock(ticker):
    """
    Dynamic stock prediction for any ticker
    """
    try:
        data = fetch_latest_data(ticker)
        verdict, confidence = predict_market(data)
        return jsonify({"ticker": ticker, "prediction": verdict, "confidence": confidence})
    except Exception as e:
        return jsonify({"error": str(e)})

# --------- Run App ---------
if __name__ == "__main__":
    app.run(debug=True)
