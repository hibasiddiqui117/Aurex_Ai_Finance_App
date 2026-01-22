# alerts.py
import json
import schedule
import time
from datetime import datetime
import threading

class AlertSystem:
    def __init__(self):
        self.alerts = []
        self.running = False
        
    def create_price_alert(self, symbol, target_price, condition='above'):
        """Create a new price alert"""
        alert = {
            'id': len(self.alerts) + 1,
            'symbol': symbol,
            'target_price': target_price,
            'condition': condition,
            'created': datetime.now().isoformat(),
            'triggered': False
        }
        self.alerts.append(alert)
        self.save_alerts()
        return alert
    
    def check_alerts(self, symbol, current_price):
        """Check if any alerts should be triggered"""
        triggered = []
        for alert in self.alerts:
            if alert['symbol'] == symbol and not alert['triggered']:
                if alert['condition'] == 'above' and current_price >= alert['target_price']:
                    alert['triggered'] = True
                    alert['triggered_at'] = datetime.now().isoformat()
                    alert['actual_price'] = current_price
                    triggered.append(alert)
                elif alert['condition'] == 'below' and current_price <= alert['target_price']:
                    alert['triggered'] = True
                    alert['triggered_at'] = datetime.now().isoformat()
                    alert['actual_price'] = current_price
                    triggered.append(alert)
        
        if triggered:
            self.save_alerts()
            self.send_notifications(triggered)
        
        return triggered
    
    def save_alerts(self):
        """Save alerts to JSON file"""
        with open('alerts.json', 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def load_alerts(self):
        """Load alerts from JSON file"""
        try:
            with open('alerts.json', 'r') as f:
                self.alerts = json.load(f)
        except FileNotFoundError:
            self.alerts = []
    
    def send_notifications(self, triggered_alerts):
        """Send notifications for triggered alerts"""
        for alert in triggered_alerts:
            print(f"ALERT! {alert['symbol']} hit {alert['target_price']} "
                  f"(Current: {alert['actual_price']})")
            # Here you can add email, SMS, or push notifications