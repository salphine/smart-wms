import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time

# Page config - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Smart WMS - Advanced Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f5f7fa;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eaeaea;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .status-good {
        background: #e1f7e1;
        color: #0a5e0a;
    }
    .status-warning {
        background: #fff3cd;
        color: #856404;
    }
    .status-critical {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Section headers */
    .section-header {
        background: white;
        border-left: 4px solid #ff4b4b;
        padding: 0.75rem 1rem;
        margin: 1.5rem 0 1rem 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .section-header h3 {
        margin: 0;
        color: #1e293b;
        font-weight: 600;
    }
    
    /* Timeline styling */
    .timeline-item {
        background: white;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #ff4b4b;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Dashboard title */
    .dashboard-title {
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Dashboard Header
st.markdown("""
<div class="dashboard-title">
    <h1 style="margin:0; font-size:2.5rem;">🏭 Smart Warehouse Management System</h1>
    <p style="margin:0.5rem 0 0 0; opacity:0.9;">Real-time RFID Inventory Tracking & Analytics</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/warehouse.png", width=80)
    st.markdown("## Control Panel")
    
    # Refresh settings
    st.markdown("### 🔄 Refresh Settings")
    auto_refresh = st.checkbox("Enable Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", min_value=5, max_value=60, value=10, step=5)
    
    # Filters
    st.markdown("### 🔍 Filters")
    
    # Zone filter
    zones = ["All Zones", "Aisle A", "Aisle B", "Aisle C", "Loading Dock", 
             "Shipping Bay", "Quality Check", "Packing Area"]
    selected_zone = st.selectbox("Location Zone", zones)
    
    # Manual refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Fetch data from API
@st.cache_data(ttl=10)
def fetch_inventory_data():
    try:
        response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching inventory: {e}")
        return None
    return None

@st.cache_data(ttl=10)
def fetch_alert_data():
    try:
        response = requests.get(f"{API_URL}/api/inventory/alerts", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

@st.cache_data(ttl=10)
def fetch_scan_data():
    try:
        response = requests.get(f"{API_URL}/api/scans/recent?limit=50", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

# Fetch all data
with st.spinner("Loading dashboard data..."):
    inventory_data = fetch_inventory_data()
    alert_data = fetch_alert_data()
    scan_data = fetch_scan_data()

# Check API connection
if inventory_data is None:
    st.error("⚠️ Cannot connect to backend API. Please ensure the server is running.")
    st.info("Start the backend with: uvicorn app.main:app --reload --port 8000")
    st.stop()

# Convert to DataFrame
if inventory_data:
    df_inventory = pd.DataFrame(inventory_data)
    
    # Debug info (can be removed later)
    with st.expander("Debug Info"):
        st.write("Inventory Data Columns:", df_inventory.columns.tolist())
        st.write("Sample Data:", df_inventory.head())
else:
    df_inventory = pd.DataFrame()

if not df_inventory.empty:
    # Calculate metrics
    total_items = df_inventory['current_quantity'].sum() if 'current_quantity' in df_inventory.columns else 0
    total_products = len(df_inventory)
    low_stock_count = len(df_inventory[df_inventory['needs_reorder'] == True]) if 'needs_reorder' in df_inventory.columns else 0
    
    # Metrics Row
    st.markdown("## 📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Products", total_products)
    with col2:
        st.metric("Total Items", int(total_items))
    with col3:
        st.metric("Low Stock Alerts", low_stock_count, delta_color="inverse")
    with col4:
        healthy_count = total_products - low_stock_count
        st.metric("Healthy Stock", healthy_count)
    with col5:
        scan_count = len(scan_data) if scan_data else 0
        st.metric("Total Scans", scan_count)
    
    st.divider()
    
    # Main Dashboard Content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        <div class="section-header">
            <h3>📈 Inventory Distribution</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple bar chart first (more reliable)
        if 'name' in df_inventory.columns and 'current_quantity' in df_inventory.columns:
            # Create color map
            colors = ['red' if x else 'green' for x in df_inventory['needs_reorder']]
            
            fig = go.Figure()
            
            # Add bar chart
            fig.add_trace(go.Bar(
                x=df_inventory['name'],
                y=df_inventory['current_quantity'],
                name='Current Stock',
                marker_color=colors,
                text=df_inventory['current_quantity'],
                textposition='outside',
            ))
            
            # Add reorder line
            fig.add_trace(go.Scatter(
                x=df_inventory['name'],
                y=df_inventory['reorder_point'],
                name='Reorder Point',
                mode='lines+markers',
                line=dict(color='orange', width=2, dash='dash'),
                marker=dict(size=8, color='orange')
            ))
            
            fig.update_layout(
                title="Current Stock Levels vs Reorder Points",
                xaxis_title="Product",
                yaxis_title="Quantity",
                height=500,
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Required columns not found in inventory data")
            st.write("Available columns:", df_inventory.columns.tolist())
    
    with col_right:
        # Low Stock Alerts
        st.markdown("""
        <div class="section-header">
            <h3>⚠️ Low Stock Alerts</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if alert_data and len(alert_data) > 0:
            for alert in alert_data:
                with st.container():
                    st.warning(f"**{alert.get('product_name', 'Unknown')}**\n\n"
                              f"Current: {alert.get('current_quantity', 0)} units\n"
                              f"Reorder at: {alert.get('reorder_point', 0)} units")
                    st.caption(f"Alert created: {alert.get('created_at', 'Just now')}")
                    st.divider()
        else:
            st.success("✅ No low stock alerts at this time")
        
        # Stock Distribution Pie Chart
        st.markdown("""
        <div class="section-header">
            <h3>🥧 Stock Distribution</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if 'needs_reorder' in df_inventory.columns:
            status_counts = df_inventory['needs_reorder'].value_counts()
            status_labels = ['Healthy Stock', 'Low Stock']
            status_values = [status_counts.get(False, 0), status_counts.get(True, 0)]
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=status_labels,
                values=status_values,
                hole=0.4,
                marker_colors=['#2ecc71', '#ff4b4b']
            )])
            fig_pie.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No distribution data available")
    
    # ===== FIXED RECENT SCANS SECTION =====
    st.markdown("""
    <div class="section-header">
        <h3>📋 Recent Scans</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if scan_data and len(scan_data) > 0:
        # Convert to DataFrame
        scan_df = pd.DataFrame(scan_data)
        
        # Create display DataFrame with safe column access
        display_cols = []
        column_mapping = {}
        
        # Map common column names
        if 'rfid_tag' in scan_df.columns:
            display_cols.append('rfid_tag')
            column_mapping['rfid_tag'] = 'RFID Tag'
        elif 'rfid' in scan_df.columns:
            display_cols.append('rfid')
            column_mapping['rfid'] = 'RFID Tag'
            
        if 'action' in scan_df.columns:
            display_cols.append('action')
            column_mapping['action'] = 'Action'
            
        if 'location' in scan_df.columns:
            display_cols.append('location')
            column_mapping['location'] = 'Location'
            
        if 'scanned_by' in scan_df.columns:
            display_cols.append('scanned_by')
            column_mapping['scanned_by'] = 'Scanner'
            
        # Handle timestamp - try different possible column names
        time_col = None
        for col in ['created_at', 'timestamp', 'time', 'scan_time']:
            if col in scan_df.columns:
                time_col = col
                break
        
        if time_col:
            try:
                # Convert to datetime and format
                scan_df['formatted_time'] = pd.to_datetime(scan_df[time_col]).dt.strftime('%Y-%m-%d %H:%M:%S')
                display_cols.append('formatted_time')
                column_mapping['formatted_time'] = 'Timestamp'
            except:
                # If conversion fails, just show original
                display_cols.append(time_col)
                column_mapping[time_col] = 'Time'
        
        # Display the scans
        if display_cols:
            st.dataframe(
                scan_df[display_cols].head(15),
                use_container_width=True,
                hide_index=True,
                column_config={col: column_mapping.get(col, col) for col in display_cols}
            )
            st.caption(f"Showing {min(15, len(scan_df))} of {len(scan_df)} recent scans")
        else:
            # Fallback: show all columns
            st.dataframe(scan_df.head(10), use_container_width=True)
            st.caption(f"Showing {min(10, len(scan_df))} recent scans")
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
                        time.sleep(1)
                        st.rerun()
                except:
                    st.error("Error adding scan")
        
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
                        time.sleep(1)
                        st.rerun()
                except:
                    st.error("Error adding scan")
        
        with col3:
            if st.button("🔄 Refresh"):
                st.cache_data.clear()
                st.rerun()
    
    # Product Health Dashboard
    st.markdown("""
    <div class="section-header">
        <h3>🏷️ Product Health Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create product health cards
    health_cols = st.columns(4)
    for idx, (_, row) in enumerate(df_inventory.iterrows()):
        with health_cols[idx % 4]:
            # Determine status
            if row['current_quantity'] == 0:
                status = "critical"
                status_text = "Out of Stock"
                status_color = "#f8d7da"
            elif row['needs_reorder']:
                status = "warning"
                status_text = "Low Stock"
                status_color = "#fff3cd"
            else:
                status = "good"
                status_text = "Healthy"
                status_color = "#e1f7e1"
            
            # Calculate health percentage
            health_pct = min(100, (row['current_quantity'] / max(row['reorder_point'], 1)) * 100)
            
            st.markdown(f"""
            <div style="background:white; border-radius:10px; padding:1rem; margin-bottom:1rem; border:1px solid #eaeaea;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <h4 style="margin:0;">{row['name']}</h4>
                    <span style="background:{status_color}; padding:0.25rem 0.75rem; border-radius:20px; font-size:0.8rem;">
                        {status_text}
                    </span>
                </div>
                <p style="margin:0.25rem 0; color:#666; font-size:0.9rem;">SKU: {row['sku']}</p>
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
    st.caption(f"🏭 Smart Warehouse Management System - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_interval)
    st.session_state.last_update = datetime.now()
    st.cache_data.clear()
    st.rerun()
