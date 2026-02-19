import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Smart WMS Dashboard",
    page_icon="🏭",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .section-header {
        background: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Title
st.title("🏭 Smart Warehouse Management System")
st.caption("Real-time inventory tracking with RFID")

# Sidebar
with st.sidebar:
    st.header("Controls")
    auto_refresh = st.checkbox("Auto-refresh (10s)", value=True)
    
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# Function to fetch data
@st.cache_data(ttl=5)
def fetch_inventory():
    try:
        response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=5)
def fetch_alerts():
    try:
        response = requests.get(f"{API_URL}/api/inventory/alerts", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=5)
def fetch_scans():
    try:
        response = requests.get(f"{API_URL}/api/scans/recent?limit=20", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# Fetch all data
inventory_data = fetch_inventory()
alert_data = fetch_alerts()
scan_data = fetch_scans()

# Check connection
if inventory_data is None:
    st.error("⚠️ Cannot connect to backend. Please ensure the server is running.")
    st.stop()

# Convert to DataFrame
df_inventory = pd.DataFrame(inventory_data) if inventory_data else pd.DataFrame()

# Metrics Row
if not df_inventory.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(df_inventory))
    with col2:
        st.metric("Total Items", int(df_inventory['current_quantity'].sum()))
    with col3:
        low_stock = len(df_inventory[df_inventory['needs_reorder'] == True])
        st.metric("Low Stock Alerts", low_stock, delta_color="inverse")
    with col4:
        st.metric("API Status", "Connected ✓")

# Main content
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Inventory Levels")
    
    if not df_inventory.empty:
        # Create bar chart
        colors = ['red' if x else 'green' for x in df_inventory['needs_reorder']]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_inventory['name'],
            y=df_inventory['current_quantity'],
            name='Current Stock',
            marker_color=colors,
            text=df_inventory['current_quantity'],
            textposition='outside',
        ))
        
        fig.add_trace(go.Scatter(
            x=df_inventory['name'],
            y=df_inventory['reorder_point'],
            name='Reorder Point',
            mode='lines+markers',
            line=dict(color='orange', width=2, dash='dash'),
            marker=dict(size=8, color='orange')
        ))
        
        fig.update_layout(
            height=400,
            hovermode='x unified',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No inventory data available")

with col_right:
    st.subheader("⚠️ Low Stock Alerts")
    
    if alert_data and len(alert_data) > 0:
        for alert in alert_data:
            st.warning(f"**{alert.get('product_name', 'Unknown')}**  \n"
                      f"Current: {alert.get('current_quantity', 0)} units  \n"
                      f"Reorder at: {alert.get('reorder_point', 0)} units")
    else:
        st.success("✅ No low stock alerts")

# RECENT SCANS SECTION - FIXED VERSION
st.subheader("📋 Recent Scans")

if scan_data and len(scan_data) > 0:
    # Convert to DataFrame
    df_scans = pd.DataFrame(scan_data)
    
    # Debug info in expander (optional)
    with st.expander("Debug Info"):
        st.write("Scan data columns:", df_scans.columns.tolist())
        st.write("Sample data:", df_scans.head())
    
    # Format the data for display
    display_df = pd.DataFrame()
    
    # Handle different possible column names
    if 'rfid_tag' in df_scans.columns:
        display_df['RFID Tag'] = df_scans['rfid_tag']
    elif 'rfid' in df_scans.columns:
        display_df['RFID Tag'] = df_scans['rfid']
    
    if 'action' in df_scans.columns:
        display_df['Action'] = df_scans['action']
    
    if 'location' in df_scans.columns:
        display_df['Location'] = df_scans['location']
    
    if 'scanned_by' in df_scans.columns:
        display_df['Scanner'] = df_scans['scanned_by']
    
    # Handle timestamp
    if 'created_at' in df_scans.columns:
        try:
            # Convert to datetime and format
            timestamps = pd.to_datetime(df_scans['created_at'])
            display_df['Time'] = timestamps.dt.strftime('%Y-%m-%d %H:%M:%S')
            display_df['Time Ago'] = timestamps.apply(
                lambda x: f"{int((datetime.now() - x).total_seconds() / 60)} min ago" 
                if (datetime.now() - x).total_seconds() < 3600 
                else f"{int((datetime.now() - x).total_seconds() / 3600)} hours ago"
            )
        except:
            display_df['Time'] = df_scans['created_at']
    
    # Display the scans
    if not display_df.empty:
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Showing {len(display_df)} recent scans")
    else:
        # Fallback: show raw data
        st.dataframe(df_scans, use_container_width=True)
else:
    # No scans found - provide option to add test scans
    st.info("No recent scans found")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Test Scan 1"):
            try:
                response = requests.post(
                    f"{API_URL}/api/scans/",
                    json={"rfid_tag": "RFID001", "location": "Loading Dock", "scanner_id": "test"}
                )
                if response.status_code == 200:
                    st.success("Scan added! Refresh to see it.")
                    st.cache_data.clear()
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("➕ Add Test Scan 2"):
            try:
                response = requests.post(
                    f"{API_URL}/api/scans/",
                    json={"rfid_tag": "RFID002", "location": "Shipping Bay", "scanner_id": "test"}
                )
                if response.status_code == 200:
                    st.success("Scan added! Refresh to see it.")
                    st.cache_data.clear()
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

# Footer
st.divider()
st.caption(f"Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh
if auto_refresh:
    time.sleep(10)
    st.cache_data.clear()
    st.rerun()
