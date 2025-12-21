import pandas as pd
import matplotlib.pyplot as plt

# Load CSV, skip first row which contains 'Ticker'
df = pd.read_csv("sp500.csv", skiprows=1, index_col=0, parse_dates=True)

# Rename columns to standard names
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Ensure all numeric columns are floats
df = df.apply(pd.to_numeric, errors='coerce')

# Drop rows with NaN just in case
df = df.dropna()
# Daily returns
df['Return'] = df['Close'].pct_change()

# Volatility (rolling std of returns)
df['Volatility'] = df['Return'].rolling(window=10).std()

# Drop NaN values created by pct_change and rolling
df = df.dropna()

print(df.head())
print(df.dtypes)

# Plot the Close price
df['Close'].plot(figsize=(12,5), title="S&P 500 Price Trend")
plt.show()
df.to_csv("cleaned_sp500_features.csv")
