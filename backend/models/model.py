import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load cleaned data
df = pd.read_csv("cleaned_sp500_features.csv", index_col=0, parse_dates=True)

# Features and target
X = df[['Return', 'Volatility']]
y = df['Target']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, shuffle=False, test_size=0.2
)

# Train RandomForest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predictions
preds = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))

# Save trained model
joblib.dump(model, "market_model.pkl")
print("Model saved as market_model.pkl")
