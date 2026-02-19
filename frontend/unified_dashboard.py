import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import time
import webbrowser
import subprocess
import sys
import os

# Page config
st.set_page_config(
    page_title="Smart WMS - Unified Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .nav-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eaeaea;
        transition: transform 0.2s;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    .nav-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border-color: #ff4b4b;
    }
    .nav-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .nav-title {
        font-weight: bold;
        margin-bottom: 0.25rem;
    }
    .nav-desc {
        font-size: 0.8rem;
        color: #666;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-online {
        background: #d4edda;
        color: #155724;
    }
    .status-offline {
        background: #f8d7da;
        color: #721c24;
    }
    .divider {
        margin: 2rem 0;
        border-top: 1px solid #eaeaea;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Check backend status
@st.cache_data(ttl=5)
def check_backend():
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            inv = requests.get(f"{API_URL}/api/inventory/levels", timeout=2)
            scans = requests.get(f"{API_URL}/api/scans/recent?limit=1", timeout=2)
            return {
                'status': 'online',
                'inventory_count': len(inv.json()) if inv.status_code == 200 else 0,
                'scan_count': len(scans.json()) if scans.status_code == 200 else 0,
                'last_check': datetime.now()
            }
    except:
        pass
    return {'status': 'offline', 'inventory_count': 0, 'scan_count': 0, 'last_check': datetime.now()}

backend = check_backend()

# Header
st.markdown(f"""
<div class="main-header">
    <h1 style="margin:0;">🏭 Smart Warehouse Management System</h1>
    <p style="margin:0.5rem 0 0 0; opacity:0.9;">Unified Dashboard - All Applications in One Place</p>
    <div style="margin-top:1rem;">
        <span class="status-badge {'status-online' if backend['status'] == 'online' else 'status-offline'}">
            Backend: {'🟢 Online' if backend['status'] == 'online' else '🔴 Offline'}
        </span>
        <span style="margin-left:1rem; color:rgba(255,255,255,0.8);">
            Last checked: {backend['last_check'].strftime('%H:%M:%S')}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Stats
if backend['status'] == 'online':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products", backend['inventory_count'])
    with col2:
        st.metric("Total Scans", backend['scan_count'])
    with col3:
        st.metric("RFID Tags", 6)
    with col4:
        st.metric("System Status", "Healthy")

# Navigation Section
st.markdown("## 🧭 Quick Navigation")

# App links in a grid
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="nav-card" onclick="window.open('http://localhost:8504', '_blank')">
        <div class="nav-icon">📊</div>
        <div class="nav-title">Main Dashboard</div>
        <div class="nav-desc">Real-time inventory tracking with charts and alerts</div>
        <div style="margin-top:0.5rem;"><span class="status-badge status-online">● Running</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-card" onclick="window.open('http://localhost:8502', '_blank')">
        <div class="nav-icon">🏠</div>
        <div class="nav-title">Landing Page</div>
        <div class="nav-desc">Professional welcome and overview</div>
        <div style="margin-top:0.5rem;"><span class="status-badge status-offline">○ Stopped</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="nav-card" onclick="window.open('http://localhost:8503', '_blank')">
        <div class="nav-icon">📦</div>
        <div class="nav-title">Inventory View</div>
        <div class="nav-desc">Detailed product management</div>
        <div style="margin-top:0.5rem;"><span class="status-badge status-offline">○ Stopped</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-card" onclick="window.open('http://localhost:8510', '_blank')">
        <div class="nav-icon">📈</div>
        <div class="nav-title">Reports & Analytics</div>
        <div class="nav-desc">Advanced reporting and trends</div>
        <div style="margin-top:0.5rem;"><span class="status-badge status-offline">○ Stopped</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="nav-card" onclick="window.open('http://localhost:8505', '_blank')">
        <div class="nav-icon">⚙️</div>
        <div class="nav-title">Settings</div>
        <div class="nav-desc">System configuration</div>
        <div style="margin-top:0.5rem;"><span class="status-badge status-offline">○ Stopped</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-card" onclick="window.open('http://localhost:8506', '_blank')">
        <div class="nav-icon">🔍</div>
        <div class="nav-title">Scan Viewer</div>
        <div class="nav-desc">Scan history and diagnostics</div>
        <div style="margin-top:0.5rem;"><span class="status-badge status-offline">○ Stopped</span></div>
    </div>
    """, unsafe_allow_html=True)

# App Launcher Section
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("## 🚀 App Launcher")
st.markdown("Click buttons below to start/stop applications")

def launch_app(port, script_name):
    try:
        subprocess.Popen(
            f'start cmd /k C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -m streamlit run {script_name} --server.port {port}',
            shell=True
        )
        return True
    except:
        return False

col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("🚀 Start Landing Page (8502)", use_container_width=True):
        if launch_app(8502, "landing_page.py"):
            st.success("Landing Page starting...")
    
    if st.button("🚀 Start Inventory View (8503)", use_container_width=True):
        if launch_app(8503, "inventory_view.py"):
            st.success("Inventory View starting...")

with col_b:
    if st.button("🚀 Start Reports (8510)", use_container_width=True):
        if launch_app(8510, "reports.py"):
            st.success("Reports starting...")
    
    if st.button("🚀 Start Settings (8505)", use_container_width=True):
        if launch_app(8505, "settings.py"):
            st.success("Settings starting...")

with col_c:
    if st.button("🚀 Start Scan Viewer (8506)", use_container_width=True):
        if launch_app(8506, "scan_diagnostic.py"):
            st.success("Scan Viewer starting...")
    
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Current Dashboard Preview
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("## 📊 Live Dashboard Preview")

# Fetch and display basic inventory data
try:
    inv_response = requests.get(f"{API_URL}/api/inventory/levels", timeout=3)
    if inv_response.status_code == 200:
        data = inv_response.json()
        df = pd.DataFrame(data)
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Current Stock Levels")
                fig = px.bar(df, x='name', y='current_quantity', 
                           color='needs_reorder',
                           color_discrete_map={True: 'red', False: 'green'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Low Stock Alerts")
                for _, row in df[df['needs_reorder'] == True].iterrows():
                    st.warning(f"**{row['name']}**: {int(row['current_quantity'])} units (Reorder at {int(row['reorder_point'])})")
except:
    st.info("Connect to backend to see live preview")

# Footer with all links
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("## 🔗 Quick Access Links")

link_cols = st.columns(3)
with link_cols[0]:
    st.markdown("""
    - [📊 Main Dashboard](http://localhost:8504)
    - [🏠 Landing Page](http://localhost:8502)
    """)
with link_cols[1]:
    st.markdown("""
    - [📦 Inventory View](http://localhost:8503)
    - [📈 Reports](http://localhost:8510)
    """)
with link_cols[2]:
    st.markdown("""
    - [⚙️ Settings](http://localhost:8505)
    - [🔍 Scan Viewer](http://localhost:8506)
    """)

# System Info
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
col_i1, col_i2, col_i3 = st.columns(3)
with col_i1:
    st.caption(f"Backend: {'Connected' if backend['status'] == 'online' else 'Disconnected'}")
with col_i2:
    st.caption(f"Python: 3.11")
with col_i3:
    st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh
time.sleep(30)
st.cache_data.clear()
st.rerun()
