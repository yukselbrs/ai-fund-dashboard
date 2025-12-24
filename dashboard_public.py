import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpaca.trading.client import TradingClient
import time

# --- CONFIG ---
st.set_page_config(page_title="Baris AI Fund", layout="wide")

# --- AUTHENTICATION (From Secrets) ---
# We use st.secrets so we don't expose keys in the code
try:
    API_KEY = st.secrets["ALPACA_KEY"]
    SECRET_KEY = st.secrets["ALPACA_SECRET"]
except:
    st.error("⚠️ API Keys Missing! Set them in Streamlit Secrets.")
    st.stop()

def get_alpaca_data():
    client = TradingClient(API_KEY, SECRET_KEY, paper=True)
    acct = client.get_account()
    positions = client.get_all_positions()
    return acct, positions

# --- LAYOUT ---
st.title("🚀 Baris AI Hedge Fund: Public Tracker")

try:
    acct, positions = get_alpaca_data()
    
    # METRICS
    equity = float(acct.equity)
    last_equity = float(acct.last_equity)
    pl_pct = (equity - last_equity) / last_equity * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Equity", f"${equity:,.2f}", f"{pl_pct:.2f}%")
    c2.metric("Buying Power", f"${float(acct.buying_power):,.2f}")
    c3.metric("Cash", f"${float(acct.cash):,.2f}")
    
    st.markdown("---")
    
    # PORTFOLIO CHART
    if positions:
        df = pd.DataFrame([{
            "Ticker": p.symbol,
            "Value": float(p.market_value),
            "Qty": float(p.qty),
            "P/L ($)": float(p.unrealized_pl),
            "P/L (%)": float(p.unrealized_plpc) * 100
        } for p in positions])
        
        # Pie Chart for Allocation
        fig = go.Figure(data=[go.Pie(labels=df['Ticker'], values=df['Value'], hole=.3)])
        fig.update_layout(height=400, title_text="Asset Allocation")
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(df.style.format({"Value": "${:,.2f}", "P/L ($)": "${:,.2f}", "P/L (%)": "{:.2f}%"}))
    else:
        st.info("Portfolio is currently 100% Cash.")

except Exception as e:
    st.error(f"Connection Error: {e}")

if st.button("🔄 Refresh Data"):
    st.experimental_rerun()