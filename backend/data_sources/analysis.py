import pandas as pd
import matplotlib.pyplot as plt

# Load raw CSV
df = pd.read_csv("sp500.csv", skiprows=1, index_col=0, parse_dates=True)

# Rename columns
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Convert to numeric
df = df.apply(pd.to_numeric, errors='coerce')

# Drop NaNs
df = df.dropna()

# Features for ML
df['Return'] = df['Close'].pct_change()
df['Volatility'] = df['Return'].rolling(30).std()

# Drop NaNs from rolling
df = df.dropna()

# Target: 1 if next day return > 0, else 0
df['Target'] = (df['Return'].shift(-1) > 0).astype(int)
df = df.dropna()  # drop last row where target is NaN

# Inspect
print(df.head())
print(df.dtypes)

# Plot
df['Close'].plot(figsize=(12,5), title="S&P 500 Price Trend")
plt.show()

# Save cleaned CSV
df.to_csv("cleaned_sp500_features.csv")
