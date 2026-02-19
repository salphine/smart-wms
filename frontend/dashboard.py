import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import time

# Page config - THIS IS KEY for full width
st.set_page_config(
    page_title="Smart WMS Dashboard",
    page_icon="🏭",
    layout="wide",  # This makes it use full width
    initial_sidebar_state="expanded"
)

# Use custom CSS to further stretch content
st.markdown("""
<style>
    .main > div {
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }
    .stApp {
        width: 100%;
    }
    .block-container {
        max-width: 100%;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

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
    zones = ["All", "Aisle A", "Aisle B", "Aisle C", "Loading Dock", "Shipping Bay", "Quality Check", "Packing Area"]
    selected_zone = st.selectbox("Select zone", zones)

# Main dashboard layout - using columns with better ratios
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

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
            
            # Display metrics with better formatting
            with col1:
                st.metric("Total Products", total_products, delta=None)
            with col2:
                st.metric("Total Items", int(total_items), delta=None)
            with col3:
                st.metric("Low Stock Alerts", low_stock_items, 
                         delta=-low_stock_items if low_stock_items > 0 else None,
                         delta_color="inverse")
            with col4:
                st.metric("API Status", "Connected ✓", delta=None)
        else:
            st.warning("No inventory data found")
    else:
        st.error(f"API Error: {response.status_code}")
except Exception as e:
    st.error(f"⚠️ Cannot connect to API. Make sure the backend server is running at {API_URL}")
    st.info("Start the backend server with: uvicorn app.main:app --reload --port 8000")

# Two-column layout for main content - wider left column for chart
left_col, right_col = st.columns([3, 1])  # 3:1 ratio gives more space to chart

with left_col:
    st.subheader("📊 Inventory Levels")
    
    try:
        response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                
                # Filter by zone if selected (if zone data available)
                if selected_zone != "All" and 'location_zone' in df.columns:
                    df_filtered = df[df['location_zone'] == selected_zone]
                else:
                    df_filtered = df
                
                # Create bar chart with better sizing
                fig = px.bar(
                    df_filtered, 
                    x='name', 
                    y='current_quantity',
                    color='needs_reorder',
                    color_discrete_map={True: 'red', False: 'green'},
                    title="Current Stock Levels by Product",
                    labels={'current_quantity': 'Quantity', 'name': 'Product'},
                    height=500  # Taller chart
                )
                fig.update_layout(
                    showlegend=False,
                    margin=dict(l=40, r=40, t=40, b=40),
                    xaxis_title="Product",
                    yaxis_title="Quantity in Stock"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No inventory data available")
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
                        st.divider()
            else:
                st.success("✅ No low stock alerts!")
    except Exception as e:
        st.info("Checking for alerts...")

# Recent scans - full width section
st.subheader("📋 Recent Scans")
st.caption("Latest RFID scan activities")

try:
    response = requests.get(f"{API_URL}/api/scans/recent?limit=20", timeout=5)
    if response.status_code == 200:
        scans = response.json()
        
        if scans:
            scan_df = pd.DataFrame(scans)
            if 'created_at' in scan_df.columns:
                scan_df['time'] = pd.to_datetime(scan_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                # Display as a full-width table
                st.dataframe(
                    scan_df[['rfid_tag', 'action', 'location', 'time']],
                    use_container_width=True,  # This makes it full width
                    hide_index=True,
                    column_config={
                        "rfid_tag": "RFID Tag",
                        "action": "Action",
                        "location": "Location",
                        "time": "Timestamp"
                    }
                )
                
                # Show count
                st.caption(f"Showing {len(scans)} recent scans")
        else:
            st.info("No recent scans")
except Exception as e:
    st.info("Waiting for scan data...")

# Auto-refresh
if auto_refresh:
    time.sleep(10)
    st.rerun()

# Footer
st.divider()
st.caption("Smart Warehouse Management System - Real-time Inventory Tracking")
