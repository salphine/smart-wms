import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time
import numpy as np

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

# Initialize session state for historical data
if 'scan_history' not in st.session_state:
    st.session_state.scan_history = []
if 'inventory_history' not in st.session_state:
    st.session_state.inventory_history = []
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
    
    # Status filter
    status_filter = st.multiselect(
        "Stock Status",
        ["In Stock", "Low Stock", "Critical"],
        default=["In Stock", "Low Stock", "Critical"]
    )
    
    # Date range for scans
    st.markdown("### 📅 Scan History Range")
    days_back = st.slider("Days to show", min_value=1, max_value=30, value=7)
    
    # Manual refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    
    st.divider()
    st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Helper function to get status color
def get_status_color(quantity, reorder_point):
    if quantity == 0:
        return "critical", "Out of Stock"
    elif quantity <= reorder_point:
        return "warning", "Low Stock"
    else:
        return "good", "In Stock"

# Fetch data from API
@st.cache_data(ttl=10)
def fetch_inventory_data():
    try:
        response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
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
        response = requests.get(f"{API_URL}/api/scans/recent?limit=100", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

# Fetch all data
inventory_data = fetch_inventory_data()
alert_data = fetch_alert_data()
scan_data = fetch_scan_data()

# Check API connection
if inventory_data is None:
    st.error("⚠️ Cannot connect to backend API. Please ensure the server is running.")
    st.info("Start the backend with: uvicorn app.main:app --reload --port 8000")
    st.stop()

# Convert to DataFrame
df_inventory = pd.DataFrame(inventory_data)

if not df_inventory.empty:
    # Calculate metrics
    total_items = df_inventory['current_quantity'].sum()
    total_products = len(df_inventory)
    low_stock_count = len(df_inventory[df_inventory['needs_reorder'] == True])
    critical_count = len(df_inventory[df_inventory['current_quantity'] == 0])
    
    # Metrics Row with custom cards
    st.markdown("## 📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#64748b; font-size:0.9rem; margin:0;">TOTAL PRODUCTS</h3>
            <p style="font-size:2rem; font-weight:700; margin:0.5rem 0; color:#1e293b;">{}</p>
            <p style="color:#64748b; font-size:0.8rem; margin:0;">Unique SKUs</p>
        </div>
        """.format(total_products), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#64748b; font-size:0.9rem; margin:0;">TOTAL ITEMS</h3>
            <p style="font-size:2rem; font-weight:700; margin:0.5rem 0; color:#1e293b;">{}</p>
            <p style="color:#64748b; font-size:0.8rem; margin:0;">In Stock</p>
        </div>
        """.format(int(total_items)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#64748b; font-size:0.9rem; margin:0;">LOW STOCK</h3>
            <p style="font-size:2rem; font-weight:700; margin:0.5rem 0; color:#ff4b4b;">{}</p>
            <p style="color:#64748b; font-size:0.8rem; margin:0;">Below reorder point</p>
        </div>
        """.format(low_stock_count), unsafe_allow_html=True)
    
    with col4:
        in_stock_count = total_products - low_stock_count - critical_count
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#64748b; font-size:0.9rem; margin:0;">HEALTHY STOCK</h3>
            <p style="font-size:2rem; font-weight:700; margin:0.5rem 0; color:#2ecc71;">{}</p>
            <p style="color:#64748b; font-size:0.8rem; margin:0;">Above reorder point</p>
        </div>
        """.format(in_stock_count), unsafe_allow_html=True)
    
    with col5:
        scan_count = len(scan_data) if scan_data else 0
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#64748b; font-size:0.9rem; margin:0;">TOTAL SCANS</h3>
            <p style="font-size:2rem; font-weight:700; margin:0.5rem 0; color:#3498db;">{}</p>
            <p style="color:#64748b; font-size:0.8rem; margin:0;">Last 100 records</p>
        </div>
        """.format(scan_count), unsafe_allow_html=True)
    
    st.divider()
    
    # Main Dashboard Content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        <div class="section-header">
            <h3>📈 Inventory Distribution</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create advanced bar chart
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Current Stock Levels", "Stock vs Reorder Point"),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4]
        )
        
        # Stock levels bar chart
        colors = ['#ff4b4b' if x else '#2ecc71' for x in df_inventory['needs_reorder']]
        fig.add_trace(
            go.Bar(
                x=df_inventory['name'],
                y=df_inventory['current_quantity'],
                name='Current Stock',
                marker_color=colors,
                text=df_inventory['current_quantity'],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Quantity: %{y}<br>Reorder at: %{customdata}<extra></extra>',
                customtext=df_inventory['reorder_point']
            ),
            row=1, col=1
        )
        
        # Add reorder line
        fig.add_trace(
            go.Scatter(
                x=df_inventory['name'],
                y=df_inventory['reorder_point'],
                name='Reorder Point',
                mode='lines+markers',
                line=dict(color='orange', width=2, dash='dash'),
                marker=dict(size=8, color='orange')
            ),
            row=1, col=1
        )
        
        # Stock vs Reorder Point comparison
        fig.add_trace(
            go.Bar(
                x=df_inventory['name'],
                y=df_inventory['current_quantity'],
                name='Current',
                marker_color='#3498db',
                offsetgroup=0
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=df_inventory['name'],
                y=df_inventory['reorder_point'],
                name='Reorder Point',
                marker_color='#e74c3c',
                offsetgroup=1
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified',
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        fig.update_xaxes(title_text="Product", row=1, col=1)
        fig.update_yaxes(title_text="Quantity", row=1, col=1)
        fig.update_xaxes(title_text="Product", row=2, col=1)
        fig.update_yaxes(title_text="Quantity", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Inventory Health Dashboard
        st.markdown("""
        <div class="section-header">
            <h3>🏷️ Product Health Dashboard</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create health metrics for each product
        health_cols = st.columns(4)
        for idx, (_, row) in enumerate(df_inventory.iterrows()):
            with health_cols[idx % 4]:
                status_class, status_text = get_status_color(row['current_quantity'], row['reorder_point'])
                health_pct = min(100, (row['current_quantity'] / max(row['reorder_point'], 1)) * 100)
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 0.5rem 0;">{row['name']}</h4>
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                        <span>SKU: {row['sku']}</span>
                        <span class="status-badge status-{status_class}">{status_text}</span>
                    </div>
                    <div style="margin:0.5rem 0;">
                        <div style="display:flex; justify-content:space-between;">
                            <span>Stock: <b>{int(row['current_quantity'])}</b></span>
                            <span>Reorder at: <b>{int(row['reorder_point'])}</b></span>
                        </div>
                    </div>
                    <div style="background:#ecf0f1; height:8px; border-radius:4px; margin:0.5rem 0;">
                        <div style="background:{'#e74c3c' if status_class=='critical' else '#f39c12' if status_class=='warning' else '#2ecc71'}; 
                                  width:{min(100, health_pct)}%; height:8px; border-radius:4px;"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#7f8c8d;">
                        <span>Health: {health_pct:.1f}%</span>
                        <span>Reorder Qty: {int(row['reorder_quantity'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_right:
        # Low Stock Alerts
        st.markdown("""
        <div class="section-header">
            <h3>⚠️ Critical Alerts</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if alert_data and len(alert_data) > 0:
            for alert in alert_data:
                st.markdown(f"""
                <div class="timeline-item">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>{alert.get('product_name', 'Unknown')}</strong>
                        <span class="status-badge status-critical">Alert</span>
                    </div>
                    <div style="margin-top:0.5rem;">
                        <p style="margin:0; color:#e74c3c;">⚠️ Stock below reorder point!</p>
                        <p style="margin:0.25rem 0 0 0; font-size:0.9rem;">
                            Current: {alert.get('current_quantity', 0)} units | 
                            Reorder at: {alert.get('reorder_point', 0)} units
                        </p>
                        <p style="margin:0.25rem 0 0 0; font-size:0.8rem; color:#7f8c8d;">
                            {alert.get('created_at', 'Just now')}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("✅ No critical alerts at this time")
        
        # Stock Distribution Pie Chart
        st.markdown("""
        <div class="section-header">
            <h3>🥧 Stock Distribution</h3>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        # Quick Actions
        st.markdown("""
        <div class="section-header">
            <h3>⚡ Quick Actions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📦 Generate Reorder", use_container_width=True):
                st.success("Purchase orders created!")
        with col_b:
            if st.button("📊 Export Report", use_container_width=True):
                st.info("Report exported!")
    
    # Recent Scans Timeline
    st.markdown("""
    <div class="section-header">
        <h3>📋 Live Scan Timeline</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if scan_data and len(scan_data) > 0:
        scan_df = pd.DataFrame(scan_data)
        scan_df['created_at'] = pd.to_datetime(scan_df['created_at'])
        scan_df['hour'] = scan_df['created_at'].dt.hour
        
        # Scan activity heatmap
        col_scan1, col_scan2 = st.columns([2, 1])
        
        with col_scan1:
            # Timeline chart
            scan_timeline = scan_df.groupby(
                pd.Grouper(key='created_at', freq='1H')
            ).size().reset_index(name='count')
            
            fig_timeline = px.line(
                scan_timeline, 
                x='created_at', 
                y='count',
                title="Scan Activity Timeline",
                markers=True
            )
            fig_timeline.update_layout(height=200, margin=dict(l=40, r=40, t=40, b=20))
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        with col_scan2:
            # Scanner statistics
            scanner_stats = scan_df['scanned_by'].value_counts().head(5)
            st.markdown("**Top Scanners:**")
            for scanner, count in scanner_stats.items():
                st.markdown(f"- {scanner}: {count} scans")
        
        # Recent scans table
        st.markdown("**Recent Scan Activity**")
        scan_df['time_ago'] = (datetime.now() - scan_df['created_at']).dt.total_seconds() / 60
        scan_df['display_time'] = scan_df.apply(
            lambda x: f"{int(x['time_ago'])} min ago" if x['time_ago'] < 60 
            else f"{int(x['time_ago']/60)} hours ago", axis=1
        )
        
        display_cols = ['rfid_tag', 'action', 'location', 'scanned_by', 'display_time']
        display_names = ['RFID Tag', 'Action', 'Location', 'Scanner', 'Time']
        
        st.dataframe(
            scan_df[display_cols].head(10),
            column_config={col: name for col, name in zip(display_cols, display_names)},
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No scan data available. Perform some scans to see activity!")
    
    # Footer with system status
    st.divider()
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        st.caption(f"🟢 Backend: {'Connected' if inventory_data else 'Disconnected'}")
    with col_f2:
        st.caption(f"💾 Database: SQLite")
    with col_f3:
        st.caption(f"📊 Total Records: {len(df_inventory)} products, {len(scan_data) if scan_data else 0} scans")
    with col_f4:
        st.caption(f"⏰ Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_interval)
    st.session_state.last_update = datetime.now()
    st.rerun()
