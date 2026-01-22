# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
import base64
from stock_predictor import StockPredictor
from financial_bot import FinancialBot
from config import Config

# Page configuration
st.set_page_config(
    page_title="AUREX",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
predictor = StockPredictor()
bot = FinancialBot()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .positive {
        color: green;
        font-weight: bold;
    }
    .negative {
        color: red;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def create_download_link(df, filename):
    """Generate a download link for DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 AUREX-Stock Market Predictor </h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Stock selection
        selected_stock = st.selectbox(
            "Select Stock",
            options=list(Config.POPULAR_STOCKS.keys()),
            index=0
        )
        symbol = Config.POPULAR_STOCKS[selected_stock]
        
        # Time period
        period = st.selectbox(
            "Time Period",
            options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
            index=3
        )
        
        # Prediction days
        prediction_days = st.slider(
            "Prediction Horizon (days)",
            min_value=1,
            max_value=30,
            value=5
        )
        
        # Update button
        update_data = st.button("🔄 Update Data", type="primary")
        
        st.markdown("---")
        st.header("📊 Quick Actions")
        if st.button("📈 Market Overview"):
            st.session_state.active_tab = "Market Overview"
        if st.button("🤖 Financial Bot"):
            st.session_state.active_tab = "Financial Bot"
        if st.button("📉 Predictions"):
            st.session_state.active_tab = "Predictions"
        if st.button("🚨 Alerts"):
            st.session_state.active_tab = "Alert System"
    
    # Initialize session state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Market Overview"
    
    # Fetch data
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_stock_data(symbol, period):
        return predictor.fetch_data(symbol, period)
    
    df = get_stock_data(symbol, period)
    
    # Main content area
    if st.session_state.active_tab == "Market Overview":
        display_market_overview(symbol, df, selected_stock)
    elif st.session_state.active_tab == "Predictions":
        display_predictions(symbol, prediction_days, selected_stock)
    elif st.session_state.active_tab == "Financial Bot":
        display_financial_bot(symbol)
    elif st.session_state.active_tab == "Alert System":
        display_alert_system(symbol)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Data from Yahoo Finance</p>
            
        </div>
        """,
        unsafe_allow_html=True
    )

def display_market_overview(symbol, df, selected_stock):
    """Display market overview tab"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📊 {selected_stock} ({symbol}) - Price Chart")
        
        if not df.empty:
            # Create interactive chart
            fig = go.Figure()
            
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ))
            
            # Add moving averages
            if 'SMA_20' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['SMA_20'],
                    line=dict(color='orange', width=1),
                    name='SMA 20'
                ))
            
            if 'SMA_50' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['SMA_50'],
                    line=dict(color='blue', width=1),
                    name='SMA 50'
                ))
            
            fig.update_layout(
                title=f'{selected_stock} Price Chart',
                yaxis_title='Price ($)',
                xaxis_title='Date',
                template='plotly_white',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Current Statistics")
        
        if not df.empty:
            current_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            st.metric(
                label="Current Price",
                value=f"${current_price:.2f}",
                delta=f"{change:.2f} ({change_pct:.2f}%)"
            )
            
            # Additional metrics
            metrics_col1, metrics_col2 = st.columns(2)
            
            with metrics_col1:
                st.metric("Open", f"${df['Open'].iloc[-1]:.2f}")
                st.metric("High", f"${df['High'].iloc[-1]:.2f}")
            
            with metrics_col2:
                st.metric("Low", f"${df['Low'].iloc[-1]:.2f}")
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,}")
            
            # Download button
            st.markdown("### 💾 Export Data")
            if st.button("Download CSV"):
                st.markdown(create_download_link(df, f"{symbol}_data.csv"), 
                           unsafe_allow_html=True)
            
            # Technical indicators
            st.markdown("### 📊 Technical Indicators")
            if len(df) > 20:
                df_with_indicators = predictor.add_technical_indicators(df.copy())
                
                rsi = df_with_indicators['RSI'].iloc[-1]
                rsi_status = "🔴 Overbought" if rsi > 70 else "🟢 Oversold" if rsi < 30 else "⚪ Neutral"
                
                st.metric("RSI (14)", f"{rsi:.2f}", rsi_status)
                
                if 'MACD' in df_with_indicators.columns:
                    macd = df_with_indicators['MACD'].iloc[-1]
                    signal = df_with_indicators['MACD_signal'].iloc[-1]
                    macd_signal = "🟢 Bullish" if macd > signal else "🔴 Bearish"
                    st.metric("MACD", f"{macd:.4f}", macd_signal)

def display_predictions(symbol, days_ahead, selected_stock):
    """Display predictions tab"""
    st.subheader(f"🔮 Price Predictions for {selected_stock}")
    
    with st.spinner("Training model and making predictions..."):
        prediction = predictor.predict(symbol, days_ahead)
    
    if prediction:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Current Price",
                f"${prediction['current_price']}",
                help="Latest closing price"
            )
        
        with col2:
            st.metric(
                f"Predicted Price ({prediction['days_ahead']} days)",
                f"${prediction['predicted_price']}",
                delta=f"{prediction['price_change_pct']}%",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "Model Confidence",
                f"{prediction['confidence']:.1f}%",
                help="Based on model accuracy"
            )
        
        # Visual representation
        fig = go.Figure()
        
        # Current price
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=prediction['current_price'],
            delta={'reference': prediction['predicted_price'], 'relative': True},
            title={"text": "Current vs Predicted"},
            domain={'row': 0, 'column': 0}
        ))
        
        fig.update_layout(
            grid={'rows': 1, 'columns': 1, 'pattern': "independent"},
            height=200
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Model information
        with st.expander("📋 Model Details"):
            st.write(f"**Last Training Date:** {prediction['training_info']['last_training_date']}")
            st.write(f"**Mean Absolute Error:** ${prediction['training_info']['mae']:.2f}")
            st.write("**Features Used:**")
            for feature in prediction['training_info']['features_used']:
                st.write(f"- {feature}")
        
        # Disclaimer
        st.warning("""
        ⚠️ **Important Notice:** 
        - Stock predictions are based on historical data and machine learning models
        - Past performance does not guarantee future results
        - Always do your own research and consult with financial advisors
        - This tool is for educational purposes only
        """)
    else:
        st.error("Could not generate predictions. Please try with a different stock or time period.")

def display_financial_bot(symbol):
    """Display financial bot tab"""
    st.subheader("🤖 Financial Bot Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 Market Summary")
        
        # Get market summary
        with st.spinner("Fetching market data..."):
            summary = bot.get_market_summary(['^GSPC', 'AAPL', 'MSFT', 'GOOGL', 'AMZN'])
        
        for stock in summary:
            change_color = "positive" if stock['change'] >= 0 else "negative"
            st.markdown(f"""
            <div class="card">
                <h4>{stock['name']} ({stock['symbol']})</h4>
                <p>Price: <strong>${stock['price']}</strong></p>
                <p>Change: <span class="{change_color}">{stock['change']} ({stock['change_pct']}%)</span></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Quick Analysis")
        
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Trend Analysis", "Volatility Check", "Support/Resistance", "Volume Analysis"]
        )
        
        if st.button("Run Analysis"):
            with st.spinner("Analyzing..."):
                # Simple analysis logic
                stock_data = predictor.fetch_data(symbol, '1mo')
                
                if not stock_data.empty:
                    latest_close = stock_data['Close'].iloc[-1]
                    avg_close = stock_data['Close'].mean()
                    
                    if analysis_type == "Trend Analysis":
                        trend = "🟢 Bullish" if latest_close > avg_close else "🔴 Bearish"
                        st.success(f"**Trend:** {trend}")
                        st.write(f"Current Price: ${latest_close:.2f}")
                        st.write(f"30-day Average: ${avg_close:.2f}")
                    
                    elif analysis_type == "Volatility Check":
                        volatility = stock_data['Close'].std()
                        st.info(f"**30-day Volatility:** ${volatility:.2f}")
                        st.write("Higher volatility indicates greater risk")
                    
                    st.write("---")
                    st.write("**Recommendation:** Consider consulting multiple analysis tools before making investment decisions.")

def display_alert_system(symbol):
    """Display alert system tab"""
    st.subheader("🚨 Price Alert System")
    
    tab1, tab2 = st.tabs(["Create Alert", "Active Alerts"])
    
    with tab1:
        st.markdown("### Set New Alert")
        
        col1, col2 = st.columns(2)
        
        with col1:
            alert_symbol = st.selectbox(
                "Stock Symbol",
                options=list(Config.POPULAR_STOCKS.values()),
                index=list(Config.POPULAR_STOCKS.values()).index(symbol) if symbol in Config.POPULAR_STOCKS.values() else 0
            )
            
            alert_type = st.selectbox(
                "Alert Type",
                options=["price_above", "price_below", "percent_change"]
            )
        
        with col2:
            if alert_type in ["price_above", "price_below"]:
                threshold = st.number_input(
                    "Price Threshold ($)",
                    min_value=0.0,
                    value=100.0,
                    step=0.01
                )
                condition = None
            else:
                threshold = st.number_input(
                    "Percentage Change (%)",
                    min_value=0.1,
                    value=5.0,
                    step=0.1
                )
                condition = st.selectbox(
                    "Direction",
                    options=["increase", "decrease"]
                )
        
        if st.button("➕ Add Alert", type="primary"):
            alert = bot.add_alert(alert_symbol, alert_type, threshold, condition)
            st.success(f"✅ Alert created for {alert_symbol} (ID: {alert['id']})")
    
    with tab2:
        st.markdown("### Active Alerts")
        
        # Check for triggered alerts
        if st.button("🔍 Check Alerts"):
            triggered = bot.check_alerts()
            if triggered:
                for alert in triggered:
                    st.error(f"""
                    🚨 **Alert Triggered!**
                    - Stock: {alert['symbol']}
                    - Type: {alert['type']}
                    - Triggered at: {alert['triggered_at']}
                    - Price: ${alert['triggered_price']}
                    """)
        
        # Display all alerts
        alerts = bot.alerts
        if alerts:
            for alert in alerts:
                status = "✅ Triggered" if alert['triggered'] else "⏳ Active"
                status_color = "red" if alert['triggered'] else "green"
                
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <h4>{alert['symbol']}</h4>
                            <p><strong>Type:</strong> {alert['type'].replace('_', ' ').title()}</p>
                            <p><strong>Threshold:</strong> {alert['threshold']}</p>
                            <p><strong>Created:</strong> {alert['created']}</p>
                        </div>
                        <div style="color: {status_color}; font-weight: bold;">
                            {status}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Remove button
                if st.button(f"Remove Alert #{alert['id']}", key=f"remove_{alert['id']}"):
                    bot.remove_alert(alert['id'])
                    st.rerun()
        else:
            st.info("No alerts set up yet. Create your first alert above!")

if __name__ == "__main__":
    main()