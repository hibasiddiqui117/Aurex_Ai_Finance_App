# financial_bot.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class FinancialBot:
    def __init__(self):
        self.alerts_file = 'alerts.json'
        self.alerts = self.load_alerts()        
    def load_alerts(self):
        """Load saved alerts from file"""
        if os.path.exists(self.alerts_file):
            with open(self.alerts_file, 'r') as f:
                return json.load(f)
        return []    
    def save_alerts(self):
        """Save alerts to file"""
        with open(self.alerts_file, 'w') as f:
            json.dump(self.alerts, f, indent=2)    
    def add_alert(self, symbol, alert_type, threshold, condition):
        """Add a new price alert"""
        alert = {
            'id': len(self.alerts) + 1,
            'symbol': symbol,
            'type': alert_type,  # 'price_above', 'price_below', 'percent_change'
            'threshold': threshold,
            'condition': condition,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'triggered': False
        }
        self.alerts.append(alert)
        self.save_alerts()
        return alert    
    def check_alerts(self):
        """Check all alerts against current prices"""
        triggered_alerts = []        
        for alert in self.alerts:
            if alert['triggered']:
                continue                
            try:
                stock = yf.Ticker(alert['symbol'])
                current_price = stock.history(period='1d')['Close'].iloc[-1]                
                is_triggered = False
                if alert['type'] == 'price_above' and current_price > alert['threshold']:
                    is_triggered = True
                elif alert['type'] == 'price_below' and current_price < alert['threshold']:
                    is_triggered = True
                elif alert['type'] == 'percent_change':
                    # Get yesterday's price
                    hist = stock.history(period='2d')
                    if len(hist) >= 2:
                        yesterday_price = hist['Close'].iloc[-2]
                        pct_change = ((current_price - yesterday_price) / yesterday_price) * 100
                        if alert['condition'] == 'increase' and pct_change > alert['threshold']:
                            is_triggered = True
                        elif alert['condition'] == 'decrease' and pct_change < -alert['threshold']:
                            is_triggered = True                
                if is_triggered:
                    alert['triggered'] = True
                    alert['triggered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    alert['triggered_price'] = current_price
                    triggered_alerts.append(alert.copy())
                    
            except Exception as e:
                print(f"Error checking alert: {e}")
        
        if triggered_alerts:
            self.save_alerts()
            
        return triggered_alerts
    
    def get_market_summary(self, symbols=None):
        """Get summary for multiple stocks"""
        if symbols is None:
            symbols = ['^GSPC', 'AAPL', 'MSFT', 'GOOGL']
        
        summary = []
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                hist = stock.history(period='5d')
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - prev_close
                    change_pct = (change / prev_close) * 100
                    
                    summary.append({
                        'symbol': symbol,
                        'name': info.get('shortName', symbol),
                        'price': round(current, 2),
                        'change': round(change, 2),
                        'change_pct': round(change_pct, 2),
                        'volume': info.get('volume', 0),
                        'market_cap': info.get('marketCap', 0)
                    })
            except:
                continue        
        return summary    
    def remove_alert(self, alert_id):
        """Remove an alert by ID"""
        self.alerts = [a for a in self.alerts if a['id'] != alert_id]
        self.save_alerts()
        return True