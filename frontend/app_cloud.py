import streamlit as st
import requests
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="Smart WMS - Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Check backend status
@st.cache_data(ttl=5)
def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if response.status_code == 200:
            try:
                inv_response = requests.get(f"{BACKEND_URL}/api/inventory/levels", timeout=3)
                if inv_response.status_code == 200:
                    products = inv_response.json()
                    return {
                        'status': 'online',
                        'inventory_count': len(products),
                        'last_check': datetime.now()
                    }
            except:
                pass
            return {'status': 'online', 'inventory_count': 0, 'last_check': datetime.now()}
    except:
        pass
    return {'status': 'offline', 'inventory_count': 0, 'last_check': datetime.now()}

backend = check_backend()

# Hero Section
st.markdown(f"""
<div class="hero">
    <h1>🏭 Smart WMS Dashboard</h1>
    <p>Warehouse Management System</p>
    <div style="margin-top: 1rem;">
        <span style="background: {'#10b981' if backend['status'] == 'online' else '#ef4444'}; color: white; padding: 0.5rem 2rem; border-radius: 50px; font-weight: bold;">
            Backend: {'🟢 Online' if backend['status'] == 'online' else '🔴 Offline'}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{backend['inventory_count']}</div>
        <div>Products in Stock</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">✅</div>
        <div>System Status</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">API</div>
        <div>FastAPI Backend</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Inventory Section
if backend['status'] == 'online':
    st.header("📦 Inventory Levels")
    try:
        response = requests.get(f"{BACKEND_URL}/api/inventory/levels", timeout=3)
        if response.status_code == 200:
            products = response.json()
            if products:
                st.dataframe(products, use_container_width=True)
            else:
                st.info("No products in inventory yet")
        else:
            st.error("Failed to fetch inventory")
    except Exception as e:
        st.error(f"Error loading inventory: {str(e)}")

    st.divider()

    # Reorder Alerts Section
    st.header("⚠️ Reorder Alerts")
    try:
        response = requests.get(f"{BACKEND_URL}/api/inventory/alerts", timeout=3)
        if response.status_code == 200:
            alerts = response.json()
            if alerts:
                st.dataframe(alerts, use_container_width=True)
            else:
                st.success("✅ No reorder alerts")
        else:
            st.error("Failed to fetch alerts")
    except Exception as e:
        st.error(f"Error loading alerts: {str(e)}")
else:
    st.warning("⚠️ Backend is offline. Please check the backend service.")
    st.info(f"Backend URL: {BACKEND_URL}")

st.divider()

# Footer
st.markdown("""
<div class="footer">
    <p>Smart WMS v1.0 | Last updated: 2026</p>
</div>
""", unsafe_allow_html=True)
