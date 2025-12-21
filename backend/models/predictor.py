# models/predictor.py
import joblib

def predict_market(data, model_path="market_model.pkl"):
    model = joblib.load(model_path)
    X_new = data[['Return', 'Volatility']].tail(1)
    pred = model.predict(X_new)[0]
    prob = model.predict_proba(X_new)[0]
    
    verdict = "UP 📈" if pred == 1 else "DOWN 📉"
    confidence = f"UP: {prob[1]:.2f}, DOWN: {prob[0]:.2f}"
    return verdict, confidence
