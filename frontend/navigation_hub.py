import streamlit as st
import subprocess
import sys
import os
import webbrowser
from datetime import datetime
import requests

# Page config
st.set_page_config(
    page_title="Smart WMS - Navigation Hub",
    page_icon="🏭",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .app-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        height: 100%;
        border: 2px solid transparent;
    }
    .app-card:hover {
        transform: translateY(-5px);
        border-color: #667eea;
    }
    .app-icon { font-size: 3rem; margin-bottom: 1rem; }
    .app-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem; }
    .app-description { color: #666; margin-bottom: 1rem; }
    .app-status {
        display: inline-block;
        padding: 0.25rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-running { background: #d4edda; color: #155724; }
    .status-stopped { background: #f8d7da; color: #721c24; }
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stat-number { font-size: 2rem; font-weight: bold; color: #667eea; }
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
        'landing': {'port': 8502, 'status': 'stopped', 'process': None},
        'dashboard': {'port': 8504, 'status': 'stopped', 'process': None},
        'inventory': {'port': 8503, 'status': 'stopped', 'process': None},
        'reports': {'port': 8510, 'status': 'stopped', 'process': None},
        'settings': {'port': 8505, 'status': 'stopped', 'process': None},
        'scan_viewer': {'port': 8506, 'status': 'stopped', 'process': None}
    }

# Check backend status
@st.cache_data(ttl=5)
def check_backend():
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            inv_response = requests.get("http://localhost:8000/api/inventory/levels", timeout=2)
            return {
                'status': 'online',
                'inventory_count': len(inv_response.json()) if inv_response.status_code == 200 else 0,
                'last_check': datetime.now()
            }
    except:
        pass
    return {'status': 'offline', 'inventory_count': 0, 'last_check': datetime.now()}

backend = check_backend()

# Hero Section
st.markdown(f"""
<div class="hero">
    <h1>🏭 Smart WMS Navigation Hub</h1>
    <p>Launch and manage all your warehouse management applications</p>
    <div style="margin-top: 1rem;">
        <span style="background: {'#10b981' if backend['status'] == 'online' else '#ef4444'}; color: white; padding: 0.5rem 2rem; border-radius: 50px;">
            Backend: {'🟢 Online' if backend['status'] == 'online' else '🔴 Offline'}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Stats
if backend['status'] == 'online':
    col1, col2, col3 = st.columns(3)
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
            <div class="stat-number">6</div>
            <div>RFID Tags</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">FastAPI</div>
            <div>Backend</div>
        </div>
        """, unsafe_allow_html=True)

def start_app(app_name, script_name, port):
    if st.session_state.apps[app_name]['status'] == 'stopped':
        try:
            if sys.platform == 'win32':
                process = subprocess.Popen(
                    f'start cmd /k C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -m streamlit run {script_name} --server.port {port}',
                    shell=True
                )
            st.session_state.apps[app_name]['status'] = 'running'
            st.session_state.apps[app_name]['process'] = process
            return True
        except Exception as e:
            st.error(f"Error starting {app_name}: {e}")
            return False
    return False

st.markdown("## 🚀 Available Applications")

# App cards
apps_config = [
    ('landing', '🏠', 'Landing Page', 'Professional welcome page', 'landing_page.py'),
    ('dashboard', '📊', 'Advanced Dashboard', 'Main inventory dashboard', 'working_dashboard.py'),
    ('inventory', '📦', 'Inventory View', 'Detailed inventory management', 'inventory_view.py'),
    ('reports', '📈', 'Reports', 'Analytics and projections', 'reports.py'),
    ('settings', '⚙️', 'Settings', 'System configuration', 'settings.py'),
    ('scan_viewer', '🔍', 'Scan Viewer', 'Scan history and diagnostics', 'scan_diagnostic.py')
]

for i in range(0, len(apps_config), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(apps_config):
            app_key, icon, title, desc, script = apps_config[i + j]
            status = st.session_state.apps[app_key]['status']
            status_text = "● Running" if status == 'running' else "○ Stopped"
            status_class = "status-running" if status == 'running' else "status-stopped"
            port = st.session_state.apps[app_key]['port']
            
            with cols[j]:
                st.markdown(f"""
                <div class="app-card">
                    <div class="app-icon">{icon}</div>
                    <div class="app-title">{title}</div>
                    <div class="app-description">{desc}</div>
                    <div><span class="app-status {status_class}">{status_text}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"▶️ Start", key=f"start_{app_key}"):
                        if start_app(app_key, script, port):
                            st.rerun()
                with col_b:
                    if st.button(f"⏹️ Stop", key=f"stop_{app_key}"):
                        st.session_state.apps[app_key]['status'] = 'stopped'
                        st.rerun()
                
                if status == 'running':
                    st.markdown(f"[🔗 Open {title}](http://localhost:{port})")

# Quick Actions
st.markdown("## ⚡ Quick Actions")
col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Check Backend"):
        st.cache_data.clear()
        st.rerun()
with col2:
    if st.button("🔄 Refresh Hub"):
        st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <h3 style="color: white;">🏭 Smart Warehouse Management System</h3>
    <p style="color: #a0aec0;">Navigation Hub - Launch any app with one click</p>
    <p style="color: #a0aec0; font-size: 0.9rem;">© 2026 Smart WMS</p>
</div>
""", unsafe_allow_html=True)
