import streamlit as st
import sys
import os
from datetime import datetime
import requests
import time

# Page config
st.set_page_config(
    page_title="Smart WMS - Navigation Hub",
    page_icon="??",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .hero h1 {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* App cards */
    .app-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        height: 100%;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .app-card:hover {
        transform: translateY(-5px);
        border-color: #667eea;
    }
    
    .app-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .app-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .app-description {
        color: #666;
        margin-bottom: 1rem;
    }
    
    .app-status {
        display: inline-block;
        padding: 0.25rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-running {
        background: #d4edda;
        color: #155724;
    }
    
    .status-stopped {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Quick stats */
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    /* Footer */
    .footer {
        background: #2d3748;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-top: 3rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'apps' not in st.session_state:
    st.session_state.apps = {
        'landing': {'port': 8501, 'status': 'stopped', 'process': None},
        'dashboard': {'port': 8502, 'status': 'stopped', 'process': None},
        'inventory': {'port': 8503, 'status': 'stopped', 'process': None},
        'reports': {'port': 8510, 'status': 'stopped', 'process': None},
        'settings': {'port': 8505, 'status': 'stopped', 'process': None},
        'scan_viewer': {'port': 8506, 'status': 'stopped', 'process': None}
    }

# Check backend status (with environment variable support for cloud deployment)
@st.cache_data(ttl=5)
def check_backend():
    try:
        # Get backend URL from environment or use localhost for development
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.get(f"{backend_url}/health", timeout=2)
        if response.status_code == 200:
            # Get additional stats
            inv_response = requests.get(f"{backend_url}/api/inventory/levels", timeout=2)
            scan_response = requests.get(f"{backend_url}/api/scans/recent?limit=1", timeout=2)
            
            return {
                'status': 'online',
                'inventory_count': len(inv_response.json()) if inv_response.status_code == 200 else 0,
                'scan_count': len(scan_response.json()) if scan_response.status_code == 200 else 0,
                'last_check': datetime.now()
            }
    except Exception as e:
        st.warning(f"Backend connection issue: {str(e)}")
    return {'status': 'offline', 'inventory_count': 0, 'scan_count': 0, 'last_check': datetime.now()}

# Get backend status
backend = check_backend()

# Hero Section
st.markdown(f"""
<div class="hero">
    <h1>?? Smart WMS Navigation Hub</h1>
    <p>Launch and manage all your warehouse management applications</p>
    <div style="margin-top: 1rem;">
        <span style="background: {'#10b981' if backend['status'] == 'online' else '#ef4444'}; color: white; padding: 0.5rem 2rem; border-radius: 50px;">
            Backend: {'?? Online' if backend['status'] == 'online' else '?? Offline'}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Stats
if backend['status'] == 'online':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{backend['inventory_count']}</div>
            <div>Products</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{backend['scan_count']}</div>
            <div>Total Scans</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">6</div>
            <div>RFID Tags</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">FastAPI</div>
            <div>Backend</div>
        </div>
        """, unsafe_allow_html=True)

# Function to start an app (Streamlit Cloud compatible)
def start_app(app_name, script_name, port):
    """In Streamlit Cloud, apps are accessible via URL navigation"""
    st.info("?? Multi-app support is available locally. For cloud deployment, navigate using the sidebar menu.")
    return False

# Function to stop an app
def stop_app(app_name):
    """In Streamlit Cloud, apps are managed automatically"""
    return False

# Main content
st.markdown("## ?? Available Applications")

# First row of apps
col1, col2, col3 = st.columns(3)

with col1:
    status = st.session_state.apps['landing']['status']
    status_text = "? Running" if status == 'running' else "? Stopped"
    status_class = "status-running" if status == 'running' else "status-stopped"
    
    st.markdown(f"""
    <div class="app-card" id="landing-card">
        <div class="app-icon">??</div>
        <div class="app-title">Landing Page</div>
        <div class="app-description">Professional welcome page with system overview and feature highlights</div>
        <div><span class="app-status {status_class}">{status_text}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("?? Start", key="start_landing", use_container_width=True):
            if start_app('landing', 'landing_page.py', 8501):
                st.success("Landing page started on port 8501!")
                st.rerun()
    with col_b:
        if st.button("?? Stop", key="stop_landing", use_container_width=True):
            if stop_app('landing'):
                st.success("Landing page stopped!")
                st.rerun()
    
    if status == 'running':
        st.markdown(f"[?? Open Landing Page](http://localhost:8501)")

with col2:
    status = st.session_state.apps['dashboard']['status']
    status_text = "? Running" if status == 'running' else "? Stopped"
    status_class = "status-running" if status == 'running' else "status-stopped"
    
    st.markdown(f"""
    <div class="app-card">
        <div class="app-icon">??</div>
        <div class="app-title">Advanced Dashboard</div>
        <div class="app-description">Main inventory dashboard with charts, alerts, and real-time updates</div>
        <div><span class="app-status {status_class}">{status_text}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("?? Start", key="start_dashboard", use_container_width=True):
            if start_app('dashboard', 'advanced_dashboard_fixed.py', 8502):
                st.success("Dashboard started on port 8502!")
                st.rerun()
    with col_b:
        if st.button("?? Stop", key="stop_dashboard", use_container_width=True):
            if stop_app('dashboard'):
                st.success("Dashboard stopped!")
                st.rerun()
    
    if status == 'running':
        st.markdown(f"[?? Open Dashboard](http://localhost:8502)")

with col3:
    status = st.session_state.apps['inventory']['status']
    status_text = "? Running" if status == 'running' else "? Stopped"
    status_class = "status-running" if status == 'running' else "status-stopped"
    
    st.markdown(f"""
    <div class="app-card">
        <div class="app-icon">??</div>
        <div class="app-title">Inventory View</div>
        <div class="app-description">Detailed inventory management with search, filters, and export</div>
        <div><span class="app-status {status_class}">{status_text}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("?? Start", key="start_inventory", use_container_width=True):
            if start_app('inventory', 'inventory_view.py', 8503):
                st.success("Inventory view started on port 8503!")
                st.rerun()
    with col_b:
        if st.button("?? Stop", key="stop_inventory", use_container_width=True):
            if stop_app('inventory'):
                st.success("Inventory view stopped!")
                st.rerun()
    
    if status == 'running':
        st.markdown(f"[?? Open Inventory](http://localhost:8503)")

# Second row of apps
col4, col5, col6 = st.columns(3)

with col4:
    status = st.session_state.apps['reports']['status']
    status_text = "? Running" if status == 'running' else "? Stopped"
    status_class = "status-running" if status == 'running' else "status-stopped"
    
    st.markdown(f"""
    <div class="app-card">
        <div class="app-icon">??</div>
        <div class="app-title">Reports & Analytics</div>
        <div class="app-description">Advanced reporting with projections, trends, and performance metrics</div>
        <div><span class="app-status {status_class}">{status_text}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("?? Start", key="start_reports", use_container_width=True):
            if start_app('reports', 'reports.py', 8510):
                st.success("Reports started on port 8510!")
                st.rerun()
    with col_b:
        if st.button("?? Stop", key="stop_reports", use_container_width=True):
            if stop_app('reports'):
                st.success("Reports stopped!")
                st.rerun()
    
    if status == 'running':
        st.markdown(f"[?? Open Reports](http://localhost:8510)")

with col5:
    status = st.session_state.apps['settings']['status']
    status_text = "? Running" if status == 'running' else "? Stopped"
    status_class = "status-running" if status == 'running' else "status-stopped"
    
    st.markdown(f"""
    <div class="app-card">
        <div class="app-icon">??</div>
        <div class="app-title">Settings</div>
        <div class="app-description">System configuration, notifications, and advanced preferences</div>
        <div><span class="app-status {status_class}">{status_text}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("?? Start", key="start_settings", use_container_width=True):
            if start_app('settings', 'settings.py', 8505):
                st.success("Settings started on port 8505!")
                st.rerun()
    with col_b:
        if st.button("?? Stop", key="stop_settings", use_container_width=True):
            if stop_app('settings'):
                st.success("Settings stopped!")
                st.rerun()
    
    if status == 'running':
        st.markdown(f"[?? Open Settings](http://localhost:8505)")

with col6:
    status = st.session_state.apps['scan_viewer']['status']
    status_text = "? Running" if status == 'running' else "? Stopped"
    status_class = "status-running" if status == 'running' else "status-stopped"
    
    st.markdown(f"""
    <div class="app-card">
        <div class="app-icon">??</div>
        <div class="app-title">Scan Viewer</div>
        <div class="app-description">Detailed scan history and diagnostic tools</div>
        <div><span class="app-status {status_class}">{status_text}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("?? Start", key="start_scan", use_container_width=True):
            if start_app('scan_viewer', 'scan_diagnostic.py', 8506):
                st.success("Scan viewer started on port 8506!")
                st.rerun()
    with col_b:
        if st.button("?? Stop", key="stop_scan", use_container_width=True):
            if stop_app('scan_viewer'):
                st.success("Scan viewer stopped!")
                st.rerun()
    
    if status == 'running':
        st.markdown(f"[?? Open Scan Viewer](http://localhost:8506)")

# Quick Actions
st.markdown("## ? Quick Actions")
col_q1, col_q2, col_q3, col_q4 = st.columns(4)

with col_q1:
    if st.button("?? Start All Apps", use_container_width=True):
        for app in ['landing', 'dashboard', 'inventory', 'reports', 'settings', 'scan_viewer']:
            ports = {'landing': 8501, 'dashboard': 8502, 'inventory': 8503, 
                    'reports': 8510, 'settings': 8505, 'scan_viewer': 8506}
            scripts = {'landing': 'landing_page.py', 'dashboard': 'advanced_dashboard_fixed.py',
                      'inventory': 'inventory_view.py', 'reports': 'reports.py',
                      'settings': 'settings.py', 'scan_viewer': 'scan_diagnostic.py'}
            start_app(app, scripts[app], ports[app])
        st.success("All apps started!")
        st.rerun()

with col_q2:
    if st.button("?? Stop All Apps", use_container_width=True):
        for app in ['landing', 'dashboard', 'inventory', 'reports', 'settings', 'scan_viewer']:
            stop_app(app)
        st.success("All apps stopped!")
        st.rerun()

with col_q3:
    if st.button("?? Check Backend", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_q4:
    if st.button("?? Refresh Hub", use_container_width=True):
        st.rerun()

# System Information
st.markdown("## ?? System Information")
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
        <h4>Application Details</h4>
        <p>? <b>Backend API:</b> http://localhost:8000</p>
        <p>? <b>Database:</b> SQLite (wms.db)</p>
        <p>? <b>RFID Tags:</b> 6 Active</p>
        <p>? <b>Products:</b> 4 Configured</p>
    </div>
    """, unsafe_allow_html=True)

with col_info2:
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
        <h4>System Status</h4>
        <p>?? <b>Backend:</b> {backend['status'].title()}</p>
        <p>?? <b>Ports:</b> 8501-8506 Available</p>
        <p>? <b>Last Check:</b> {backend['last_check'].strftime('%H:%M:%S')}</p>
        <p>?? <b>Platform:</b> {sys.platform}</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <h3 style="color: white;">?? Smart Warehouse Management System</h3>
    <p style="color: #a0aec0;">Multi-App Navigation Hub | All applications run independently</p>
    <p style="color: #a0aec0; font-size: 0.9rem;">© 2026 - Salphine chemos smart warehouse system</p>
</div>
""", unsafe_allow_html=True)
