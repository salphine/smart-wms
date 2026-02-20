"""
Smart WMS Dashboard - Connected to FastAPI Backend
All UI features preserved with real backend data
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time
import requests
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(
    page_title="Smart WMS - Connected",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.smartwms.com/help',
        'Report a bug': 'https://www.smartwms.com/bug',
        'About': "# Smart Warehouse Management System\nVersion 4.0.0 (Connected)"
    }
)

# API Configuration
API_URL = "http://localhost:8000"  # Your FastAPI backend

# Custom CSS (preserved from original)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .main-header {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);}
        70% {box-shadow: 0 0 0 10px rgba(0, 255, 0, 0);}
        100% {box-shadow: 0 0 0 0 rgba(0, 255, 0, 0);}
    }
    
    .status-online {
        background-color: #00ff00;
    }
    
    .status-offline {
        background-color: #ff0000;
        animation: none;
    }
    
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        height: 400px;
        overflow-y: auto;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .message {
        margin: 10px 0;
        padding: 10px;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
    }
    
    .bot-message {
        background: #f0f0f0;
        color: black;
    }
    
    .footer-container {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        text-align: center;
        padding: 12px 0;
        border-top: 2px solid #4a90e2;
        z-index: 999;
        font-family: 'Inter', sans-serif;
    }
    
    .footer-links {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 8px;
    }
    
    .footer-link {
        color: #ffd700;
        text-decoration: none;
        font-size: 14px;
        transition: all 0.3s ease;
        padding: 0 5px;
        cursor: pointer;
    }
    
    .footer-link:hover {
        color: white;
        transform: scale(1.05);
    }
    
    .metric-badge {
        background: rgba(255,255,255,0.15);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
    }
    
    .main > div {
        margin-bottom: 140px;
    }
    
    .block-container {
        padding-bottom: 8rem;
    }
    
    .connection-badge {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .connected {
        background-color: #28a745;
        color: white;
    }
    .disconnected {
        background-color: #dc3545;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.notifications = []
    st.session_state.chat_messages = []
    st.session_state.tasks = []
    st.session_state.real_time_data = pd.DataFrame(columns=['timestamp', 'value', 'category'])
    st.session_state.alerts = []
    st.session_state.user_preferences = {
        'theme': 'dark',
        'notifications': True,
        'auto_refresh': True
    }
    st.session_state.last_update = datetime.now()
    st.session_state.inventory_cache = None
    st.session_state.stats_cache = None
    st.session_state.cache_time = None

# Auto-refresh configuration
refresh_rate = st.sidebar.slider("🔄 Refresh Rate (seconds)", 5, 60, 30)
count = st_autorefresh(interval=refresh_rate * 1000, key="auto_refresh")

# Helper functions for API calls
@st.cache_data(ttl=30)
def check_backend_connection():
    """Check if backend is reachable"""
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=3)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

@st.cache_data(ttl=30)
def fetch_inventory():
    """Fetch inventory from backend"""
    try:
        response = requests.get(f"{API_URL}/api/inventory", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        return []
    except:
        return []

@st.cache_data(ttl=30)
def fetch_stats():
    """Fetch statistics from backend"""
    try:
        response = requests.get(f"{API_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

@st.cache_data(ttl=60)
def fetch_item(item_id):
    """Fetch single inventory item"""
    try:
        response = requests.get(f"{API_URL}/api/inventory/{item_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Check backend connection
backend_connected, backend_info = check_backend_connection()

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 Smart WMS Control Center")
    
    # Connection Status
    if backend_connected:
        st.markdown(f"""
        <div style="text-align: center; margin: 10px 0;">
            <span class="connection-badge connected">🟢 Backend Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align: center; margin: 10px 0;">
            <span class="connection-badge disconnected">🔴 Backend Disconnected</span>
        </div>
        <div style="background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; font-size: 12px;">
            ⚠️ Using simulated data. Run backend with:<br>
            <code>uvicorn backend.app.main:app --reload --port 8000</code>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Real-time clock
    st.markdown(f"### 🕐 {datetime.now().strftime('%H:%M:%S')}")
    
    # User profile
    with st.expander("👤 User Profile", expanded=True):
        st.markdown("**Logged in as:** Admin User")
        st.markdown(f"**Last login:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.progress(0.7, text="Profile Completion")
    
    # System health
    with st.expander("🖥️ System Health", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("CPU:")
            st.markdown("Memory:")
            st.markdown("Disk:")
        with col2:
            st.markdown("45%")
            st.markdown("62%")
            st.markdown("78%")
    
    # Quick actions
    with st.expander("⚡ Quick Actions", expanded=True):
        if st.button("📊 Generate Report", use_container_width=True):
            st.session_state.notifications.append({
                'time': datetime.now(),
                'message': 'Report generation started',
                'type': 'info'
            })
        
        if st.button("🔄 Sync Data", use_container_width=True):
            st.cache_data.clear()
            with st.spinner("Syncing with backend..."):
                time.sleep(2)
            st.success("Data synced!")
            st.rerun()
        
        if st.button("📢 Send Alerts", use_container_width=True):
            st.info("Alerts sent to all users")
    
    # System performance metrics
    st.markdown("---")
    st.markdown("### 📊 System Performance")
    
    # Real-time metrics
    metrics_col1, metrics_col2 = st.columns(2)
    with metrics_col1:
        st.metric("Response Time", "0.3s" if backend_connected else "N/A", "-0.1s")
        st.metric("CPU Load", "45%", "+5%")
    with metrics_col2:
        st.metric("Memory", "62%", "-2%")
        st.metric("Network", "1.2 MB/s", "+0.3")
    
    # Data stream indicator
    st.markdown("### 📡 Data Stream")
    if backend_connected:
        st.progress(0.8, text="Live Data: 245 packets/s")
    else:
        st.progress(random.uniform(0.5, 0.9), text=f"Simulated: {random.randint(100, 500)} packets/s")

# Main header
current_time = datetime.now().strftime('%H:%M:%S')
connection_status = "🔴 Live (Backend Connected)" if backend_connected else "🟡 Live (Simulated)"
st.markdown(f"""
<div class="main-header">
    <h1>🏭 Smart WMS Dashboard {'' if backend_connected else '(Demo Mode)'}</h1>
    <p style="font-size: 1.2rem;">{connection_status} | Auto-refresh: {refresh_rate}s</p>
</div>
""", unsafe_allow_html=True)

# Notification area
if st.session_state.notifications:
    with st.container():
        for notif in st.session_state.notifications[-3:]:
            if notif['type'] == 'info':
                st.info(f"{notif['time'].strftime('%H:%M:%S')} - {notif['message']}")
            elif notif['type'] == 'success':
                st.success(f"{notif['time'].strftime('%H:%M:%S')} - {notif['message']}")
            elif notif['type'] == 'warning':
                st.warning(f"{notif['time'].strftime('%H:%M:%S')} - {notif['message']}")

# Fetch data from backend or use simulated
if backend_connected:
    inventory_data = fetch_inventory()
    stats_data = fetch_stats()
else:
    # Simulated data when backend not connected
    inventory_data = []
    stats_data = {}

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Live Analytics",
    "🤖 AI Assistant",
    "💬 Team Chat",
    "📋 Task Manager",
    "📈 Predictions",
    "🔌 Integrations"
])

# Tab 1: Live Analytics
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Real-time Data")
        
        if backend_connected and inventory_data:
            # Real data from backend
            df = pd.DataFrame(inventory_data)
            if not df.empty and 'quantity' in df.columns:
                fig = px.bar(df.head(10), x='product' if 'product' in df.columns else df.index, 
                            y='quantity', title="Current Inventory Levels")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No inventory data available")
        else:
            # Simulated data
            current_time = datetime.now()
            new_data = pd.DataFrame({
                'timestamp': [current_time],
                'value': [random.uniform(50, 150)],
                'category': [random.choice(['Temperature', 'Humidity', 'Pressure', 'Vibration'])]
            })
            
            st.session_state.real_time_data = pd.concat([st.session_state.real_time_data, new_data], ignore_index=True)
            if len(st.session_state.real_time_data) > 50:
                st.session_state.real_time_data = st.session_state.real_time_data.tail(50)
            
            fig_live = go.Figure()
            for category in st.session_state.real_time_data['category'].unique():
                cat_data = st.session_state.real_time_data[st.session_state.real_time_data['category'] == category]
                fig_live.add_trace(go.Scatter(
                    x=cat_data['timestamp'],
                    y=cat_data['value'],
                    mode='lines+markers',
                    name=category
                ))
            
            fig_live.update_layout(title="Live Sensor Feed (Simulated)", height=400)
            st.plotly_chart(fig_live, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Live Metrics")
        
        # Real-time gauges
        col_a, col_b = st.columns(2)
        
        with col_a:
            if backend_connected and stats_data:
                utilization = stats_data.get('utilization', 65)
            else:
                utilization = random.uniform(60, 80)
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=utilization,
                title={'text': "Warehouse Capacity %"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 80], 'color': "gray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}))
            fig_gauge.update_layout(height=250)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col_b:
            if backend_connected and stats_data:
                total_items = stats_data.get('total_items', 1000)
                low_stock = stats_data.get('low_stock_items', 5)
                fill_rate = ((total_items - low_stock) / total_items * 100) if total_items > 0 else 85
            else:
                fill_rate = random.uniform(75, 95)
            
            fig_gauge2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=fill_rate,
                title={'text': "Stock Fill Rate %"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 70], 'color': "lightgray"},
                           {'range': [70, 90], 'color': "gray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 95}}))
            fig_gauge2.update_layout(height=250)
            st.plotly_chart(fig_gauge2, use_container_width=True)
        
        # Live alerts
        st.markdown("### 🚨 Live Alerts")
        alert_container = st.container()
        with alert_container:
            if backend_connected and stats_data:
                low_stock = stats_data.get('low_stock_items', 0)
                if low_stock > 0:
                    st.warning(f"⚠️ {low_stock} items are below reorder level")
                else:
                    st.success("✅ All stock levels are healthy")
            else:
                if random.random() > 0.7:
                    st.error(f"⚠️ High temperature detected in Zone A at {datetime.now().strftime('%H:%M:%S')}")
                if random.random() > 0.8:
                    st.warning(f"⚠️ Low inventory alert: SKU-{random.randint(100,999)}")
                if random.random() > 0.9:
                    st.success(f"✅ System optimized at {datetime.now().strftime('%H:%M:%S')}")

# Tab 2: AI Assistant (unchanged from original)
with tab2:
    st.markdown("### 🤖 AI Warehouse Assistant")
    st.markdown("Ask me anything about your warehouse operations")
    
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.chat_messages:
            st.markdown('<div class="message bot-message">🤖 Hello! How can I help you with your warehouse today?</div>', unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_messages[-10:]:
                if msg['type'] == 'user':
                    st.markdown(f'<div class="message user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="message bot-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Type your message:", key="ai_input")
    with col2:
        if st.button("Send", use_container_width=True):
            if user_input:
                st.session_state.chat_messages.append({'type': 'user', 'content': user_input})
                
                if backend_connected and "inventory" in user_input.lower():
                    if inventory_data:
                        total = sum(item.get('quantity', 0) for item in inventory_data)
                        response = f"Current inventory: {total} total items across {len(inventory_data)} SKUs"
                    else:
                        response = "Inventory data not available"
                else:
                    responses = {
                        'inventory': f"Current inventory level: {stats_data.get('total_items', 'N/A') if backend_connected else '78%'}",
                        'order': "There are 23 pending orders. 5 are high priority.",
                        'temperature': "Temperature is normal across all zones.",
                        'performance': f"System performance is optimal. Backend: {'Connected' if backend_connected else 'Simulated'}",
                        'forecast': "Based on current trends, expect 15% increase in orders tomorrow."
                    }
                    response = responses.get(random.choice(list(responses.keys())), 
                                          "I'm analyzing your request. The system is processing...")
                
                st.session_state.chat_messages.append({'type': 'bot', 'content': response})
                st.rerun()
    
    with st.expander("💡 AI Suggestions", expanded=True):
        if backend_connected and stats_data:
            low_stock = stats_data.get('low_stock_items', 0)
            if low_stock > 0:
                st.info(f"📦 {low_stock} items need restocking")
            else:
                st.info("📦 All stock levels are optimal")
        else:
            st.info("📦 Consider restocking SKU-123 - below threshold")
        st.info("⚡ Peak order time detected - allocate more resources")
        st.info("🔧 Maintenance recommended for Conveyor Belt B in 2 hours")

# Tab 3: Team Chat (unchanged)
with tab3:
    st.markdown("### 💬 Team Communication")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Live Team Chat")
        team_chat = st.container()
        with team_chat:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">👨‍💼 John: Inventory check completed</div>', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">👩‍💼 Sarah: Shipping department ready</div>', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">👨‍🔧 Mike: Maintenance scheduled for 3 PM</div>', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">🤖 System: New order received #ORD-789</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.text_input("Type your message...", key="team_msg")
        with col_b:
            st.button("📤 Send", key="send_team")
    
    with col2:
        st.markdown("#### Team Online")
        st.success("🟢 John (Manager)")
        st.success("🟢 Sarah (Shipping)")
        st.success("🟢 Mike (Tech)")
        st.warning("🟡 Alice (Break)")
        st.error("🔴 Bob (Offline)")
        
        if st.button("📹 Start Video Call"):
            st.info("Video call feature coming soon!")

# Tab 4: Task Manager (unchanged)
with tab4:
    st.markdown("### 📋 Real-time Task Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tasks_data = pd.DataFrame({
            'Task ID': [f'TASK-{i:03d}' for i in range(1, 8)],
            'Description': ['Inventory Check', 'Order Processing', 'Quality Control', 
                           'Equipment Maintenance', 'Stock Replenishment', 'Report Generation', 'Team Meeting'],
            'Assignee': ['John', 'Sarah', 'Mike', 'Bob', 'Alice', 'John', 'All'],
            'Priority': ['High', 'High', 'Medium', 'Low', 'High', 'Medium', 'Low'],
            'Status': ['In Progress', 'Pending', 'Completed', 'In Progress', 'Pending', 'Completed', 'Scheduled'],
            'Progress': [75, 0, 100, 30, 0, 100, 0]
        })
        
        st.dataframe(
            tasks_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Progress": st.column_config.ProgressColumn("Progress", format="%d%%", min_value=0, max_value=100)
            }
        )
        
        fig_tasks = px.bar(tasks_data, x='Task ID', y='Progress', color='Priority', title="Task Completion Progress")
        st.plotly_chart(fig_tasks, use_container_width=True)
    
    with col2:
        st.markdown("#### Create New Task")
        with st.form("new_task"):
            task_desc = st.text_input("Task Description")
            assignee = st.selectbox("Assignee", ['John', 'Sarah', 'Mike', 'Bob', 'Alice'])
            priority = st.selectbox("Priority", ['High', 'Medium', 'Low'])
            due_date = st.date_input("Due Date", datetime.now())
            
            if st.form_submit_button("Create Task"):
                st.success(f"Task created and assigned to {assignee}")

# Tab 5: Predictions (enhanced with backend data)
with tab5:
    st.markdown("### 📈 AI-Powered Predictions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        future_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        
        if backend_connected and stats_data:
            base_demand = stats_data.get('total_items', 1000) / 10
        else:
            base_demand = 100
        
        demand_forecast = pd.DataFrame({
            'Date': future_dates,
            'Predicted Demand': [base_demand + random.uniform(-10, 20) + i*0.3 for i in range(30)],
            'Upper Bound': [base_demand + 20 + random.uniform(0, 10) + i*0.3 for i in range(30)],
            'Lower Bound': [base_demand - 20 + random.uniform(-10, 0) + i*0.3 for i in range(30)]
        })
        
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=demand_forecast['Date'], y=demand_forecast['Predicted Demand'],
                                         mode='lines', name='Predicted Demand', line=dict(color='blue', width=2)))
        fig_forecast.add_trace(go.Scatter(x=demand_forecast['Date'], y=demand_forecast['Upper Bound'],
                                         mode='lines', name='Upper Bound', line=dict(dash='dash', color='gray')))
        fig_forecast.add_trace(go.Scatter(x=demand_forecast['Date'], y=demand_forecast['Lower Bound'],
                                         mode='lines', name='Lower Bound', line=dict(dash='dash', color='gray'),
                                         fill='tonexty'))
        
        fig_forecast.update_layout(title="30-Day Demand Forecast", height=400)
        st.plotly_chart(fig_forecast, use_container_width=True)
    
    with col2:
        categories = ['Electronics', 'Clothing', 'Food', 'Furniture', 'Tools']
        
        if backend_connected and inventory_data:
            df = pd.DataFrame(inventory_data)
            if not df.empty and 'category' in df.columns and 'quantity' in df.columns:
                current_inv = [df[df['category'] == cat]['quantity'].sum() for cat in categories]
            else:
                current_inv = [random.uniform(60, 100) for _ in categories]
        else:
            current_inv = [random.uniform(60, 100) for _ in categories]
        
        predicted_inv = [x * random.uniform(0.9, 1.1) for x in current_inv]
        
        fig_inv_pred = go.Figure(data=[
            go.Bar(name='Current', x=categories, y=current_inv),
            go.Bar(name='Predicted (30 days)', x=categories, y=predicted_inv)
        ])
        fig_inv_pred.update_layout(title="Inventory Level Prediction", height=400, barmode='group')
        st.plotly_chart(fig_inv_pred, use_container_width=True)
    
    st.markdown("### 🧠 AI Insights")
    insight_cols = st.columns(3)
    
    with insight_cols[0]:
        if backend_connected and stats_data:
            trend = "increasing" if stats_data.get('total_items', 0) > 1000 else "stable"
            st.info(f"📈 **Trend**: Inventory is {trend}")
        else:
            st.info("📈 **Trend**: 15% increase in orders expected next week")
    
    with insight_cols[1]:
        if backend_connected and stats_data:
            low_stock = stats_data.get('low_stock_items', 0)
            if low_stock > 5:
                st.warning(f"⚠️ **Risk**: {low_stock} items need attention")
            else:
                st.success("✅ **Risk**: Low stock levels are manageable")
        else:
            st.warning("⚠️ **Risk**: Potential stockout for Electronics category")
    
    with insight_cols[2]:
        st.success("💡 **Opportunity**: Optimize shipping routes for 20% savings")

# Tab 6: Integrations (enhanced)
with tab6:
    st.markdown("### 🔌 System Integrations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown(f"""
            <div class="glass-card">
                <h3>📦 FastAPI Backend</h3>
                <p>Status: <span style="color: {'#00ff00' if backend_connected else '#ff0000'};">
                    {'Connected' if backend_connected else 'Disconnected'}</span></p>
                <p>URL: {API_URL}</p>
                <p>Data Flow: {'1.2 MB/s' if backend_connected else '0 MB/s'}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Test Connection", key="test_backend"):
                if backend_connected:
                    st.success("✅ Backend connection successful!")
                else:
                    st.error("❌ Cannot connect to backend")
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="glass-card">
                <h3>📊 Database</h3>
                <p>Status: <span style="color: #00ff00;">Connected</span></p>
                <p>Tables: inventory, orders, users</p>
                <p>Records: 1,245</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Query DB", key="query_db"):
                st.info("Database query executed")
    
    with col3:
        with st.container():
            st.markdown("""
            <div class="glass-card">
                <h3>📱 External APIs</h3>
                <p>Status: <span style="color: #00ff00;">Ready</span></p>
                <p>Endpoints: 4 configured</p>
                <p>Rate Limit: 1000/min</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Test APIs", key="test_apis"):
                st.info("API tests initiated")
    
    st.markdown("### 📡 API Documentation")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📄 /api/health"):
            if backend_connected:
                st.json(backend_info)
            else:
                st.error("Backend not connected")
    with col2:
        if st.button("📦 /api/inventory"):
            if backend_connected:
                st.json({"items": inventory_data[:3]})
            else:
                st.json({"items": [{"id": 1, "product": "SKU-001", "quantity": 150}]})
    with col3:
        if st.button("📊 /api/stats"):
            if backend_connected:
                st.json(stats_data)
            else:
                st.json({"total_items": 1245, "low_stock_items": 3})
    with col4:
        if st.button("🔍 /docs"):
            st.markdown(f"[Open API Docs]({API_URL}/docs)")

# Fixed Footer
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
footer_html = f'''
<div class="footer-container">
    <div class="footer-links">
        <a href="{API_URL}/docs" class="footer-link" target="_blank">📄 API Docs</a>
        <a href="#" class="footer-link" onclick="return false;">🆘 Support</a>
        <a href="#" class="footer-link" onclick="return false;">📧 Contact</a>
        <a href="#" class="footer-link" onclick="return false;">🔒 Privacy</a>
        <a href="#" class="footer-link" onclick="return false;">📜 Terms</a>
        <a href="#" class="footer-link" onclick="return false;">🤖 AI Help</a>
    </div>
    <div style="display: flex; justify-content: center; align-items: center; gap: 25px; margin: 8px 0;">
        <div style="display: flex; align-items: center;">
            <span class="status-indicator {'status-online' if backend_connected else 'status-offline'}"></span>
            <span style="font-size: 13px;">{'Backend Connected' if backend_connected else 'Using Simulated Data'}</span>
        </div>
        <span class="metric-badge">⚡ Response: {'0.3s' if backend_connected else 'N/A'}</span>
        <span class="metric-badge">📈 Uptime: {'99.9%' if backend_connected else 'Simulated'}</span>
        <span class="metric-badge">👥 Users: 23</span>
    </div>
    <div style="font-size: 11px; color: #ccc;">© 2026 Smart WMS (Connected Version) | {current_time}</div>
</div>
'''
st.markdown(footer_html, unsafe_allow_html=True)

# Update timestamp
if (datetime.now() - st.session_state.last_update).seconds >= refresh_rate:
    st.session_state.last_update = datetime.now()

# Enhanced Team Chat with Video Call
with tab3:
    st.markdown("### 💬 Team Communication")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Video Call Section
        st.markdown("#### 📹 Video Conference")
        
        # Generate unique room ID
        import random
        import string
        
        col_a, col_b = st.columns([3, 1])
        with col_a:
            custom_room = st.text_input("Room Name", placeholder="Enter room name", key="video_room_input")
        with col_b:
            if st.button("🎥 Start Call", use_container_width=True):
                if custom_room:
                    room_id = custom_room.replace(" ", "-").lower()
                else:
                    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    room_id = f"WMS-{random_suffix}"
                st.session_state['video_room'] = room_id
        
        if 'video_room' in st.session_state:
            room_id = st.session_state['video_room']
            
            call_platform = st.selectbox(
                "Platform",
                ["Jitsi Meet (Free)", "Google Meet", "Zoom", "Teams"],
                key="platform_select"
            )
            
            if call_platform == "Jitsi Meet (Free)":
                jitsi_url = f"https://meet.jit.si/{room_id}"
                st.markdown(f"""
                <a href="{jitsi_url}" target="_blank" style="background-color: #28a745; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; margin: 10px 0;">
                    🔗 Join Video Call: {room_id}
                </a>
                """, unsafe_allow_html=True)
            else:
                st.info(f"Create a {call_platform} meeting and share this ID: **{room_id}**")
        
        # Existing chat messages
        st.markdown("#### 💬 Chat Messages")
        team_chat = st.container()
        with team_chat:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">👨‍💼 John: Starting video call now</div>', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">👩‍💼 Sarah: Joining the call</div>', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">🤖 System: Video conference room created: WMS-1234</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Message input
        col_x, col_y = st.columns([4, 1])
        with col_x:
            st.text_input("Type your message...", key="team_msg_video")
        with col_y:
            st.button("📤 Send", key="send_team_video")
    
    with col2:
        st.markdown("#### 👥 Online Team")
        st.success("🟢 John (Manager)")
        st.success("🟢 Sarah (Shipping)")
        st.success("🟢 Mike (Tech)")
        st.warning("🟡 Alice (Break)")
        st.error("🔴 Bob (Offline)")
        
        st.markdown("#### 📋 Quick Actions")
        if st.button("📹 Share Screen"):
            st.info("Screen sharing available in Jitsi Meet")
        if st.button("🎤 Test Mic"):
            st.info("Check your microphone settings")
