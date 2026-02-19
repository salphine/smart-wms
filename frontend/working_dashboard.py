import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time

# Page config
st.set_page_config(
    page_title="Smart WMS - Dashboard",
    page_icon="🏭",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #f5f7fa; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eaeaea;
    }
    .section-header {
        background: white;
        border-left: 4px solid #ff4b4b;
        padding: 0.75rem 1rem;
        margin: 1.5rem 0 1rem 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .section-header h3 { margin: 0; color: #1e293b; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Header
st.title("🏭 Smart Warehouse Management System")
st.caption("Real-time RFID Inventory Tracking & Analytics")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/warehouse.png", width=80)
    st.markdown("## Control Panel")
    
    auto_refresh = st.checkbox("Enable Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 10)
    
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Fetch data functions
@st.cache_data(ttl=10)
def fetch_inventory():
    try:
        r = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

@st.cache_data(ttl=10)
def fetch_alerts():
    try:
        r = requests.get(f"{API_URL}/api/inventory/alerts", timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

@st.cache_data(ttl=10)
def fetch_scans():
    try:
        r = requests.get(f"{API_URL}/api/scans/recent?limit=50", timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

# Load data
inventory_data = fetch_inventory()
alert_data = fetch_alerts()
scan_data = fetch_scans()

# Check connection
if inventory_data is None:
    st.error("⚠️ Cannot connect to backend API")
    st.stop()

# Convert to DataFrame
df_inventory = pd.DataFrame(inventory_data) if inventory_data else pd.DataFrame()

if not df_inventory.empty:
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total Products", len(df_inventory))
    with col2: st.metric("Total Items", int(df_inventory['current_quantity'].sum()))
    with col3: 
        low = len(df_inventory[df_inventory['needs_reorder'] == True])
        st.metric("Low Stock Alerts", low, delta_color="inverse")
    with col4: st.metric("Healthy Stock", len(df_inventory) - low)
    with col5: st.metric("Total Scans", len(scan_data) if scan_data else 0)

    st.divider()

    # Main charts
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Inventory Levels")
        colors = ['red' if x else 'green' for x in df_inventory['needs_reorder']]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_inventory['name'], y=df_inventory['current_quantity'],
                            marker_color=colors, text=df_inventory['current_quantity'],
                            textposition='outside', name='Current Stock'))
        fig.add_trace(go.Scatter(x=df_inventory['name'], y=df_inventory['reorder_point'],
                                mode='lines+markers', line=dict(color='orange', width=2, dash='dash'),
                                marker=dict(size=8, color='orange'), name='Reorder Point'))
        fig.update_layout(height=500, hovermode='x unified', showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("⚠️ Low Stock Alerts")
        if alert_data:
            for alert in alert_data[:5]:
                st.warning(f"**{alert.get('product_name', 'Unknown')}**  \n"
                          f"Current: {alert.get('current_quantity', 0)} units")
        else:
            st.success("✅ No low stock alerts")

    # ===== SIMPLIFIED RECENT SCANS SECTION =====
    st.subheader("📋 Recent Scans")
    
    if scan_data and len(scan_data) > 0:
        # Convert to DataFrame
        scan_df = pd.DataFrame(scan_data)
        
        # Create a clean display dataframe
        display_data = []
        for scan in scan_data[:15]:  # Show last 15 scans
            row = {}
            # Get RFID tag
            if 'rfid_tag' in scan:
                row['RFID Tag'] = scan['rfid_tag']
            elif 'rfid' in scan:
                row['RFID Tag'] = scan['rfid']
            else:
                row['RFID Tag'] = 'N/A'
            
            # Get location
            row['Location'] = scan.get('location', 'N/A')
            
            # Get scanner
            row['Scanner'] = scan.get('scanned_by', 'N/A')
            
            # Format time
            if 'created_at' in scan:
                try:
                    dt = pd.to_datetime(scan['created_at'])
                    row['Time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Calculate time ago
                    now = datetime.now()
                    diff = (now - dt).total_seconds()
                    if diff < 60:
                        row['Time Ago'] = f"{int(diff)} sec ago"
                    elif diff < 3600:
                        row['Time Ago'] = f"{int(diff/60)} min ago"
                    else:
                        row['Time Ago'] = f"{int(diff/3600)} hours ago"
                except:
                    row['Time'] = str(scan['created_at'])
                    row['Time Ago'] = 'N/A'
            else:
                row['Time'] = 'N/A'
                row['Time Ago'] = 'N/A'
            
            display_data.append(row)
        
        # Create and show dataframe
        display_df = pd.DataFrame(display_data)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(display_df)} recent scans")
        
        # Add debug expander if needed
        with st.expander("Debug - Raw Scan Data"):
            st.json(scan_data[:3])
            
    else:
        st.info("No recent scans found")
        
        # Add scan buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Add Scan 1 (RFID001)"):
                try:
                    r = requests.post(f"{API_URL}/api/scans/",
                                     json={"rfid_tag": "RFID001", "location": "Loading Dock", "scanner_id": "test"})
                    if r.status_code == 200:
                        st.success("Scan added!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                except: st.error("Error")
        
        with col2:
            if st.button("➕ Add Scan 2 (RFID002)"):
                try:
                    r = requests.post(f"{API_URL}/api/scans/",
                                     json={"rfid_tag": "RFID002", "location": "Shipping Bay", "scanner_id": "test"})
                    if r.status_code == 200:
                        st.success("Scan added!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                except: st.error("Error")
        
        with col3:
            if st.button("🔄 Refresh"):
                st.cache_data.clear()
                st.rerun()

    # Product Health Dashboard
    st.subheader("🏷️ Product Health Dashboard")
    health_cols = st.columns(4)
    for idx, (_, row) in enumerate(df_inventory.iterrows()):
        with health_cols[idx % 4]:
            status = "critical" if row['current_quantity'] == 0 else "warning" if row['needs_reorder'] else "good"
            status_text = "Out of Stock" if row['current_quantity'] == 0 else "Low Stock" if row['needs_reorder'] else "Healthy"
            status_color = "#f8d7da" if status == "critical" else "#fff3cd" if status == "warning" else "#e1f7e1"
            health_pct = min(100, (row['current_quantity'] / max(row['reorder_point'], 1)) * 100)
            
            st.markdown(f"""
            <div style="background:white; border-radius:10px; padding:1rem; margin-bottom:1rem; border:1px solid #eaeaea;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <h4 style="margin:0;">{row['name']}</h4>
                    <span style="background:{status_color}; padding:0.25rem 0.75rem; border-radius:20px; font-size:0.8rem;">
                        {status_text}
                    </span>
                </div>
                <p style="margin:0.25rem 0; color:#666;">SKU: {row['sku']}</p>
                <div style="margin:0.75rem 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>Stock: <b>{int(row['current_quantity'])}</b></span>
                        <span>Reorder at: <b>{int(row['reorder_point'])}</b></span>
                    </div>
                </div>
                <div style="background:#ecf0f1; height:6px; border-radius:3px;">
                    <div style="background:{'#e74c3c' if status=='critical' else '#f39c12' if status=='warning' else '#2ecc71'}; 
                              width:{health_pct}%; height:6px; border-radius:3px;"></div>
                </div>
                <p style="margin:0.5rem 0 0 0; font-size:0.8rem; color:#7f8c8d; text-align:right;">
                    Health: {health_pct:.1f}%
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.divider()
    st.caption(f"Smart WMS - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.session_state.last_update = datetime.now()
    st.cache_data.clear()
    st.rerun()
