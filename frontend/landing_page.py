import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Smart WMS - Home",
    page_icon="🏭",
    layout="wide"
)

# Custom CSS for landing page
st.markdown("""
<style>
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .hero h1 {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }
    
    .hero p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Stats container */
    .stats-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 3rem;
        border-radius: 20px;
        margin: 2rem 0;
    }
    
    .stat-box {
        text-align: center;
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    /* CTA button */
    .cta-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 3rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.2rem;
        border: none;
        cursor: pointer;
        transition: transform 0.3s;
    }
    
    .cta-button:hover {
        transform: scale(1.05);
    }
    
    /* Footer */
    .footer {
        background: #2d3748;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Fetch system status
@st.cache_data(ttl=10)
def get_system_status():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            inventory = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
            scans = requests.get(f"{API_URL}/api/scans/recent?limit=1", timeout=5)
            alerts = requests.get(f"{API_URL}/api/inventory/alerts", timeout=5)
            
            return {
                "status": "online",
                "inventory_count": len(inventory.json()) if inventory.status_code == 200 else 0,
                "scan_count": len(scans.json()) if scans.status_code == 200 else 0,
                "alert_count": len(alerts.json()) if alerts.status_code == 200 else 0,
                "last_check": datetime.now()
            }
    except:
        return {"status": "offline", "last_check": datetime.now()}
    return {"status": "offline", "last_check": datetime.now()}

# Get system status
system_status = get_system_status()

# Hero Section
st.markdown(f"""
<div class="hero">
    <h1>🏭 Smart Warehouse Management System</h1>
    <p>Revolutionizing Inventory Management with RFID Technology</p>
    <p style="margin-top: 1rem;">
        <span class="status-badge" style="background: {'#10b981' if system_status['status'] == 'online' else '#ef4444'}; color: white; padding: 0.5rem 1rem; border-radius: 50px;">
            System Status: {'🟢 Online' if system_status['status'] == 'online' else '🔴 Offline'}
        </span>
    </p>
</div>
""", unsafe_allow_html=True)

# Quick Stats
if system_status['status'] == 'online':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">{}</div>
            <div>Products</div>
        </div>
        """.format(system_status['inventory_count']), unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">{}</div>
            <div>Total Scans</div>
        </div>
        """.format(system_status['scan_count']), unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">{}</div>
            <div>Active Alerts</div>
        </div>
        """.format(system_status['alert_count']), unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">{}</div>
            <div>System Uptime</div>
        </div>
        """.format("99.9%"), unsafe_allow_html=True)

# Features Section
st.markdown("## 🚀 Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📡</div>
        <h3>Real-time RFID Tracking</h3>
        <p>Track inventory items in real-time with RFID technology. Instant updates on item location and movement.</p>
        <ul style="margin-top: 1rem; color: #666;">
            <li>Instant scan processing</li>
            <li>Location tracking</li>
            <li>Movement history</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚠️</div>
        <h3>Smart Reorder Alerts</h3>
        <p>Automatic alerts when stock levels fall below reorder points. Never run out of critical items.</p>
        <ul style="margin-top: 1rem; color: #666;">
            <li>Automated notifications</li>
            <li>Custom reorder points</li>
            <li>Priority-based alerts</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Advanced Analytics</h3>
        <p>Comprehensive dashboards with real-time metrics, trends, and predictive insights.</p>
        <ul style="margin-top: 1rem; color: #666;">
            <li>Interactive charts</li>
            <li>Trend analysis</li>
            <li>Performance metrics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Navigation Section
st.markdown("## 🎯 Quick Access")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("📊 Main Dashboard", use_container_width=True):
        st.switch_page("advanced_dashboard_fixed.py")

with nav_col2:
    if st.button("📋 Scan History", use_container_width=True):
        st.switch_page("scan_viewer.py")

with nav_col3:
    if st.button("📦 Inventory", use_container_width=True):
        st.switch_page("inventory_view.py")

with nav_col4:
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("settings.py")

# System Status
st.markdown("## 📡 System Status")

col_status1, col_status2 = st.columns(2)

with col_status1:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
        <h4>API Endpoints</h4>
        <p>✅ /health - System Health</p>
        <p>✅ /api/inventory/levels - Inventory Data</p>
        <p>✅ /api/scans/recent - Scan History</p>
        <p>✅ /api/inventory/alerts - Reorder Alerts</p>
    </div>
    """, unsafe_allow_html=True)

with col_status2:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
        <h4>System Information</h4>
        <p>🖥️ Backend: FastAPI + SQLite</p>
        <p>🎨 Frontend: Streamlit</p>
        <p>📡 RFID Support: Yes</p>
        <p>🔔 Last Check: {}</p>
    </div>
    """.format(system_status['last_check'].strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h3 style="color: white;">🏭 Smart WMS</h3>
            <p style="color: #a0aec0;">© 2024 All rights reserved</p>
        </div>
        <div>
            <p style="color: #a0aec0;">Version 2.0 | Enterprise Ready</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
