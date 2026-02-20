import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import time

st.set_page_config(
    page_title="Smart WMS Dashboard",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Smart Warehouse Management System")
st.caption("Real-time Inventory Tracking with RFID")

API_URL = "http://localhost:8000"

with st.sidebar:
    st.header("Controls")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_rate = st.slider("Refresh rate (seconds)", 5, 60, 10)
    
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

@st.cache_data(ttl=10)
def fetch_inventory():
    try:
        response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

@st.cache_data(ttl=10)
def fetch_alerts():
    try:
        response = requests.get(f"{API_URL}/api/inventory/alerts", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

@st.cache_data(ttl=10)
def fetch_scans():
    try:
        response = requests.get(f"{API_URL}/api/scans/recent?limit=20", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

@st.cache_data
def get_demo_data():
    return pd.DataFrame({
        "Product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
        "SKU": ["LAP001", "MOU001", "KEY001", "MON001"],
        "Current Stock": [2, 2, 1, 1],
        "Reorder Point": [3, 5, 4, 2],
        "Status": ["Low Stock", "Low Stock", "Low Stock", "Low Stock"]
    })

col1, col2, col3, col4 = st.columns(4)

inventory_data = fetch_inventory()

if inventory_data:
    df = pd.DataFrame(inventory_data)
    st.success("✅ Connected to backend API")
else:
    df = get_demo_data()
    st.warning("⚠️ Using demo data - Backend not connected")

if not df.empty:
    with col1:
        st.metric("Total Products", len(df))
    with col2:
        total = df["Current Stock"].sum() if "Current Stock" in df.columns else df["current_quantity"].sum()
        st.metric("Total Items", int(total))
    with col3:
        if "Status" in df.columns:
            low = len(df[df["Status"] == "Low Stock"])
        else:
            low = len(df[df["needs_reorder"] == True])
        st.metric("Low Stock Alerts", low)
    with col4:
        scan_count = len(fetch_scans()) if fetch_scans() else 12
        st.metric("Recent Scans", scan_count)

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Inventory Levels")
    
    x_col = "Product" if "Product" in df.columns else "name"
    y_col = "Current Stock" if "Current Stock" in df.columns else "current_quantity"
    color_col = "Status" if "Status" in df.columns else "needs_reorder"
    
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title="Current Stock Levels",
        color_discrete_map={"Low Stock": "red", "Healthy": "green", True: "red", False: "green"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("⚠️ Low Stock Alerts")
    
    alerts = fetch_alerts()
    if alerts:
        for alert in alerts[:5]:
            st.warning(f"**{alert.get('product_name', 'Unknown')}**  \nStock: {alert.get('current_quantity', 0)} units")
    else:
        for product in ["Laptop", "Mouse", "Keyboard", "Monitor"]:
            st.warning(f"**{product}**  \nStock: Low - Reorder needed")

st.subheader("📋 Recent Scans")
scans = fetch_scans()
if scans:
    scan_df = pd.DataFrame(scans[:10])
    st.dataframe(scan_df, use_container_width=True)
else:
    demo_scans = pd.DataFrame({
        "RFID Tag": ["RFID001", "RFID002", "RFID003", "RFID004"],
        "Location": ["Loading Dock", "Shipping Bay", "Quality Check", "Packing Area"],
        "Time": ["2 min ago", "15 min ago", "1 hour ago", "2 hours ago"]
    })
    st.dataframe(demo_scans, use_container_width=True)

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()

st.divider()
st.caption(f"Smart WMS v1.0 | Running on Streamlit Cloud | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
