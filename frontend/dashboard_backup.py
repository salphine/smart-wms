import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Smart WMS Dashboard",
    page_icon="🏭",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Title
st.title("🏭 Smart Warehouse Management System")
st.markdown("Real-time inventory tracking with RFID")

# Sidebar
with st.sidebar:
    st.header("Controls")
    auto_refresh = st.checkbox("Auto-refresh (10s)", value=True)
    
    st.header("Filter by Zone")
    zones = ["All", "Aisle A", "Aisle B", "Aisle C", "Loading Dock"]
    selected_zone = st.selectbox("Select zone", zones)

# Main dashboard layout
col1, col2, col3, col4 = st.columns(4)

try:
    # Fetch inventory levels
    response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
    if response.status_code == 200:
        inventory_data = response.json()
        df = pd.DataFrame(inventory_data)
        
        if not df.empty:
            # Calculate metrics
            total_products = len(df)
            total_items = df['current_quantity'].sum()
            low_stock_items = len(df[df['needs_reorder'] == True])
            
            # Display metrics
            with col1:
                st.metric("Total Products", total_products)
            with col2:
                st.metric("Total Items", int(total_items))
            with col3:
                st.metric("Low Stock Alerts", low_stock_items, 
                         delta=-low_stock_items if low_stock_items > 0 else None,
                         delta_color="inverse")
            with col4:
                st.metric("API Status", "Connected ✓")
        else:
            st.warning("No inventory data found")
    else:
        st.error(f"API Error: {response.status_code}")
except Exception as e:
    st.error(f"⚠️ Cannot connect to API. Make sure the backend server is running at {API_URL}")
    st.info("Start the backend server with: uvicorn app.main:app --reload --port 8000")

# Two-column layout
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📊 Inventory Levels")
    
    try:
        response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        if response.status_code == 200 and not df.empty:
            # Filter by zone if selected
            if selected_zone != "All" and 'location_zone' in df.columns:
                df_filtered = df[df['location_zone'] == selected_zone]
            else:
                df_filtered = df
            
            # Create bar chart
            fig = px.bar(
                df_filtered, 
                x='name', 
                y='current_quantity',
                color='needs_reorder',
                color_discrete_map={True: 'red', False: 'green'},
                title="Current Stock Levels by Product",
                labels={'current_quantity': 'Quantity', 'name': 'Product'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Waiting for data...")

with right_col:
    st.subheader("⚠️ Low Stock Alerts")
    
    try:
        response = requests.get(f"{API_URL}/api/inventory/alerts", timeout=5)
        if response.status_code == 200:
            alerts = response.json()
            
            if alerts:
                for alert in alerts:
                    with st.container():
                        st.warning(f"**{alert.get('product_name', 'Unknown')}**\n\n"
                                  f"Current: {alert.get('current_quantity', 0)} units\n"
                                  f"Reorder at: {alert.get('reorder_point', 0)} units")
            else:
                st.success("✅ No low stock alerts!")
    except:
        pass

# Recent scans
st.subheader("📋 Recent Scans")
try:
    response = requests.get(f"{API_URL}/api/scans/recent?limit=10", timeout=5)
    if response.status_code == 200:
        scans = response.json()
        
        if scans:
            scan_df = pd.DataFrame(scans)
            if 'created_at' in scan_df.columns:
                scan_df['time'] = pd.to_datetime(scan_df['created_at']).dt.strftime('%H:%M:%S')
                st.dataframe(
                    scan_df[['rfid_tag', 'action', 'location', 'time']],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No recent scans")
except Exception as e:
    st.info("Waiting for scan data...")

# Auto-refresh
if auto_refresh:
    time.sleep(10)
    st.rerun()
