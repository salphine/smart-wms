"""
Advanced Real-Time Dashboard with Multiple Applications
Smart Warehouse Management System - Fixed & Enhanced Version
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
import hashlib
import string

# Check if streamlit-autorefresh is installed, if not, provide fallback
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False
    st.warning("⚠️ For auto-refresh feature, install: pip install streamlit-autorefresh")

# Page configuration
st.set_page_config(
    page_title="Smart WMS - Advanced Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.smartwms.com/help',
        'Report a bug': 'https://www.smartwms.com/bug',
        'About': "# Smart Warehouse Management System\nVersion 3.0.0"
    }
)

# Custom CSS for advanced styling
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated header */
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
    
    /* Glass morphism cards */
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
    
    /* Metric cards */
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
    
    /* Status indicators */
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
    
    /* Chat container */
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
    
    /* Footer styling */
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
    
    /* Adjust main content for footer */
    .main > div {
        margin-bottom: 140px;
    }
    
    .block-container {
        padding-bottom: 8rem;
    }
    
    /* Video call section */
    .video-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .meeting-link {
        background-color: #ffd700;
        color: #1e3c72;
        padding: 10px 20px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
    }
    
    .meeting-link:hover {
        background-color: #ffed4e;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.login_attempts = 0
    st.session_state.notifications = []
    st.session_state.chat_messages = []
    st.session_state.team_chat_messages = [
        {"user": "John", "message": "Inventory check completed", "time": datetime.now() - timedelta(minutes=5)},
        {"user": "Sarah", "message": "Shipping department ready", "time": datetime.now() - timedelta(minutes=3)},
        {"user": "Mike", "message": "Maintenance scheduled for 3 PM", "time": datetime.now() - timedelta(minutes=1)},
        {"user": "System", "message": "New order received #ORD-789", "time": datetime.now()}
    ]
    st.session_state.tasks = []
    st.session_state.real_time_data = pd.DataFrame(columns=['timestamp', 'value', 'category'])
    st.session_state.alerts = []
    st.session_state.user_preferences = {
        'theme': 'dark',
        'notifications': True,
        'auto_refresh': True
    }
    st.session_state.last_update = datetime.now()
    st.session_state.current_room = None
    st.session_state.show_meeting_options = False
    st.session_state.sensor_history = []

# Auto-refresh configuration
refresh_rate = st.sidebar.slider("🔄 Refresh Rate (seconds)", 1, 60, 5)

# Handle auto-refresh
if AUTOREFRESH_AVAILABLE:
    count = st_autorefresh(interval=refresh_rate * 1000, key="auto_refresh")
else:
    # Fallback: Use a placeholder
    st.sidebar.info("Auto-refresh requires streamlit-autorefresh package")

# Sidebar with real-time info
with st.sidebar:
    st.markdown("## 🤖 AI Control Center")
    
    # Real-time clock
    st.markdown(f"### 🕐 {datetime.now().strftime('%H:%M:%S')}")
    
    # User profile
    with st.expander("👤 User Profile", expanded=True):
        st.markdown("**Logged in as:** Admin User")
        st.markdown(f"**Last login:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.progress(0.7, text="Profile Completion 70%")
    
    # System health
    with st.expander("🔧 System Health", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("CPU:")
            st.markdown("Memory:")
            st.markdown("Disk:")
        with col2:
            cpu_usage = random.randint(40, 60)
            memory_usage = random.randint(55, 75)
            disk_usage = random.randint(70, 85)
            st.markdown(f"{cpu_usage}%")
            st.markdown(f"{memory_usage}%")
            st.markdown(f"{disk_usage}%")
    
    # Quick actions
    with st.expander("⚡ Quick Actions", expanded=True):
        if st.button("📊 Generate Report", width='stretch'):
            st.session_state.notifications.append({
                'time': datetime.now(),
                'message': 'Report generation started',
                'type': 'info'
            })
            st.success("Report generation started!")
        
        if st.button("🔄 Sync Data", width='stretch'):
            with st.spinner("Syncing..."):
                time.sleep(2)
            st.success("Data synced!")
        
        if st.button("📢 Send Alerts", width='stretch'):
            st.info("Alerts sent to all users")
    
    # System performance metrics
    st.markdown("---")
    st.markdown("### 📊 System Performance")
    
    # Real-time metrics
    metrics_col1, metrics_col2 = st.columns(2)
    with metrics_col1:
        st.metric("Response Time", "0.3s", "-0.1s")
        st.metric("CPU Load", f"{cpu_usage}%", "+5%")
    with metrics_col2:
        st.metric("Memory", f"{memory_usage}%", "-2%")
        st.metric("Network", "1.2 MB/s", "+0.3")
    
    # Data stream indicator
    st.markdown("### 📡 Data Stream")
    st.progress(random.uniform(0.5, 0.9), text=f"Live Data: {random.randint(100, 500)} packets/s")

# Main header
st.markdown(f"""
<div class="main-header">
    <h1>🏭 Advanced Smart WMS Dashboard</h1>
    <p style="font-size: 1.2rem;">Real-time warehouse management with AI-powered insights and automation</p>
    <div style="display: flex; gap: 20px; margin-top: 20px;">
        <span>🔴 Live</span>
        <span>📊 Real-time Analytics</span>
        <span>🤖 AI Assistant</span>
        <span>🔄 Auto-refresh: {refresh_rate}s</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Notification area
if st.session_state.notifications:
    with st.container():
        for notif in st.session_state.notifications[-3:]:
            if notif['type'] == 'info':
                st.info(f"ℹ️ {notif['time'].strftime('%H:%M:%S')} - {notif['message']}")
            elif notif['type'] == 'success':
                st.success(f"✅ {notif['time'].strftime('%H:%M:%S')} - {notif['message']}")
            elif notif['type'] == 'warning':
                st.warning(f"⚠️ {notif['time'].strftime('%H:%M:%S')} - {notif['message']}")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Live Analytics",
    "🤖 AI Assistant", 
    "💬 Team Chat",
    "✅ Task Manager",
    "🔮 Predictions",
    "🔌 Integrations",
    "📹 Video Call"
])

# Tab 1: Live Analytics
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Real-time Sensor Data")
        
        # Simulate real-time data
        current_time = datetime.now()
        categories = ['Temperature', 'Humidity', 'Pressure', 'Vibration']
        values = {
            'Temperature': random.uniform(20, 30),
            'Humidity': random.uniform(40, 80),
            'Pressure': random.uniform(980, 1020),
            'Vibration': random.uniform(0, 10)
        }
        
        new_data = pd.DataFrame({
            'timestamp': [current_time],
            'value': [values[random.choice(categories)]],
            'category': [random.choice(categories)]
        })
        
        st.session_state.real_time_data = pd.concat([st.session_state.real_time_data, new_data], ignore_index=True)
        if len(st.session_state.real_time_data) > 50:
            st.session_state.real_time_data = st.session_state.real_time_data.tail(50)
        
        # Live line chart
        if not st.session_state.real_time_data.empty:
            fig_live = go.Figure()
            for category in st.session_state.real_time_data['category'].unique():
                cat_data = st.session_state.real_time_data[st.session_state.real_time_data['category'] == category]
                if not cat_data.empty:
                    fig_live.add_trace(go.Scatter(
                        x=cat_data['timestamp'],
                        y=cat_data['value'],
                        mode='lines+markers',
                        name=category
                    ))
            
            fig_live.update_layout(
                title="Live Sensor Feed",
                xaxis_title="Time",
                yaxis_title="Value",
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig_live, width='stretch')
        else:
            st.info("Collecting sensor data...")
    
    with col2:
        st.markdown("### 📈 Live Metrics")
        
        # Real-time gauges
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Temperature gauge
            temp = values['Temperature']
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=temp,
                title={'text': "Temperature °C"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [None, 50]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 20], 'color': "lightgray"},
                           {'range': [20, 30], 'color': "gray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 40}}))
            fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge, width='stretch')
        
        with col_b:
            # Humidity gauge
            humidity = values['Humidity']
            fig_gauge2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=humidity,
                title={'text': "Humidity %"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 80], 'color': "gray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}))
            fig_gauge2.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge2, width='stretch')
        
        # Live alerts
        st.markdown("### ⚠️ Live Alerts")
        alert_container = st.container()
        with alert_container:
            if random.random() > 0.7:
                st.error(f"🔥 High temperature detected in Zone A at {datetime.now().strftime('%H:%M:%S')}")
            if random.random() > 0.8:
                st.warning(f"📦 Low inventory alert: SKU-{random.randint(100,999)}")
            if random.random() > 0.9:
                st.success(f"✅ System optimized at {datetime.now().strftime('%H:%M:%S')}")

# Tab 2: AI Assistant
with tab2:
    st.markdown("### 🤖 AI Warehouse Assistant")
    st.markdown("Ask me anything about your warehouse operations")
    
    # Chat interface
    chat_container = st.container()
    with chat_container:
        # Create a container for chat messages with custom styling
        chat_html = '<div class="chat-container">'
        
        # Display chat messages
        if not st.session_state.chat_messages:
            chat_html += '<div class="message bot-message">🤖 Hello! How can I help you with your warehouse today?</div>'
        else:
            for msg in st.session_state.chat_messages[-10:]:
                if msg['type'] == 'user':
                    chat_html += f'<div class="message user-message">👤 {msg["content"]}</div>'
                else:
                    chat_html += f'<div class="message bot-message">🤖 {msg["content"]}</div>'
        
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Type your message:", key="ai_input")
    with col2:
        if st.button("Send", width='stretch'):
            if user_input:
                st.session_state.chat_messages.append({'type': 'user', 'content': user_input})
                
                # AI responses based on keywords
                user_input_lower = user_input.lower()
                if 'inventory' in user_input_lower:
                    response = "Current inventory level is 78% of capacity. Low stock items: SKU-123, SKU-456"
                elif 'order' in user_input_lower:
                    response = "There are 23 pending orders. 5 are high priority."
                elif 'temperature' in user_input_lower:
                    response = "Temperature is normal across all zones. Zone B is showing slight variation."
                elif 'performance' in user_input_lower:
                    response = "System performance is optimal. Response time: 0.3s"
                elif 'forecast' in user_input_lower:
                    response = "Based on current trends, expect 15% increase in orders tomorrow."
                else:
                    responses = [
                        "I'm analyzing your request. The system is processing...",
                        "Based on current data, I recommend checking the inventory levels.",
                        "All systems are operating normally.",
                        "I've noted your request and will alert the team."
                    ]
                    response = random.choice(responses)
                
                st.session_state.chat_messages.append({'type': 'bot', 'content': response})
                st.rerun()
    
    # AI suggestions
    with st.expander("💡 AI Suggestions", expanded=True):
        st.info("📦 Consider restocking SKU-123 - below threshold")
        st.info("⚡ Peak order time detected - allocate more resources")
        st.info("🔧 Maintenance recommended for Conveyor Belt B in 2 hours")

# Tab 3: Team Chat
with tab3:
    st.markdown("### 💬 Team Communication")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Team chat
        st.markdown("#### Live Team Chat")
        
        # Chat messages
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.team_chat_messages[-8:]:
            time_str = msg['time'].strftime('%H:%M')
            if msg['user'] == 'System':
                chat_html += f'<div class="message bot-message">🤖 {msg["user"]}: {msg["message"]} ({time_str})</div>'
            else:
                chat_html += f'<div class="message bot-message">👤 {msg["user"]}: {msg["message"]} ({time_str})</div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Message input
        col_a, col_b = st.columns([4, 1])
        with col_a:
            team_message = st.text_input("Type your message...", key="team_msg")
        with col_b:
            if st.button("📤 Send", key="send_team", width='stretch'):
                if team_message:
                    st.session_state.team_chat_messages.append({
                        "user": "You",
                        "message": team_message,
                        "time": datetime.now()
                    })
                    st.rerun()
    
    with col2:
        st.markdown("#### Team Online")
        st.success("🟢 Salphine Chemos (Manager)")
        st.success("🟢 Kelvin Glance  (Shipping)")
        st.success("🟢 Mike Kibet (Tech)")
        st.warning("🟡 Brendah Chepkoech(Break)")
        st.error("🔴 Broivin wasama (Offline)")
        
        st.markdown("#### Quick Actions")
        if st.button("📹 Start Video Call", width='stretch'):
            st.session_state.show_meeting_options = True
            st.rerun()
        if st.button("📢 Broadcast Message", width='stretch'):
            st.info("Broadcast sent to all team members")

# Tab 4: Task Manager
with tab4:
    st.markdown("### ✅ Real-time Task Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Task list
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
            width='stretch',
            hide_index=True,
            column_config={
                "Progress": st.column_config.ProgressColumn(
                    "Progress",
                    format="%d%%",
                    min_value=0,
                    max_value=100
                )
            }
        )
        
        # Task progress visualization
        if not tasks_data.empty:
            fig_tasks = px.bar(
                tasks_data,
                x='Task ID',
                y='Progress',
                color='Priority',
                title="Task Completion Progress",
                color_discrete_map={'High': 'red', 'Medium': 'orange', 'Low': 'green'}
            )
            st.plotly_chart(fig_tasks, width='stretch')
    
    with col2:
        st.markdown("#### Create New Task")
        with st.form("new_task"):
            task_desc = st.text_input("Task Description")
            assignee = st.selectbox("Assignee", ['John', 'Sarah', 'Mike', 'Bob', 'Alice'])
            priority = st.selectbox("Priority", ['High', 'Medium', 'Low'])
            due_date = st.date_input("Due Date", datetime.now())
            
            if st.form_submit_button("Create Task", width='stretch'):
                st.success(f"Task created and assigned to {assignee}")

# Tab 5: Predictions
with tab5:
    st.markdown("### 🔮 AI-Powered Predictions")
    
    # Prediction charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Demand forecast
        future_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        base_demand = 100
        trend = np.linspace(0, 15, 30)
        seasonal = 10 * np.sin(np.linspace(0, 4*np.pi, 30))
        noise = np.random.normal(0, 5, 30)
        
        demand_forecast = pd.DataFrame({
            'Date': future_dates,
            'Predicted Demand': base_demand + trend + seasonal + noise,
            'Upper Bound': base_demand + trend + seasonal + noise + 15,
            'Lower Bound': base_demand + trend + seasonal + noise - 15
        })
        
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(
            x=demand_forecast['Date'],
            y=demand_forecast['Predicted Demand'],
            mode='lines',
            name='Predicted Demand',
            line=dict(color='blue', width=2)
        ))
        fig_forecast.add_trace(go.Scatter(
            x=demand_forecast['Date'],
            y=demand_forecast['Upper Bound'],
            mode='lines',
            name='Upper Bound',
            line=dict(dash='dash', color='gray'),
            showlegend=True
        ))
        fig_forecast.add_trace(go.Scatter(
            x=demand_forecast['Date'],
            y=demand_forecast['Lower Bound'],
            mode='lines',
            name='Lower Bound',
            line=dict(dash='dash', color='gray'),
            fill='tonexty',
            showlegend=True
        ))
        
        fig_forecast.update_layout(
            title="30-Day Demand Forecast",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_forecast, width='stretch')
    
    with col2:
        # Inventory prediction
        categories = ['Electronics', 'Clothing', 'Food', 'Furniture', 'Tools']
        current_inv = [random.uniform(60, 100) for _ in categories]
        predicted_inv = [x * random.uniform(0.8, 1.2) for x in current_inv]
        
        fig_inv_pred = go.Figure(data=[
            go.Bar(name='Current', x=categories, y=current_inv, marker_color='blue'),
            go.Bar(name='Predicted (30 days)', x=categories, y=predicted_inv, marker_color='orange')
        ])
        fig_inv_pred.update_layout(
            title="Inventory Level Prediction",
            height=400,
            barmode='group',
            yaxis_title="Inventory Level %"
        )
        st.plotly_chart(fig_inv_pred, width='stretch')
    
    # AI Insights
    st.markdown("### 💡 AI Insights")
    insight_cols = st.columns(3)
    
    with insight_cols[0]:
        st.info("📈 **Trend**: 15% increase in orders expected next week")
    with insight_cols[1]:
        st.warning("⚠️ **Risk**: Potential stockout for Electronics category")
    with insight_cols[2]:
        st.success("💰 **Opportunity**: Optimize shipping routes for 20% savings")

# Tab 6: Integrations
with tab6:
    st.markdown("### 🔌 System Integrations")
    
    # Integration cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="glass-card">
                <h3>📊 ERP System</h3>
                <p>Status: <span style="color: #00ff00;">✅ Connected</span></p>
                <p>Last Sync: 2 minutes ago</p>
                <p>Data Flow: 1.2 MB/s</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Sync Now", key="sync_erp", width='stretch'):
                st.success("ERP sync initiated")
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="glass-card">
                <h3>📈 BI Tools</h3>
                <p>Status: <span style="color: #00ff00;">✅ Connected</span></p>
                <p>Last Export: 5 minutes ago</p>
                <p>Reports: 12 generated today</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Export Data", key="export_bi", width='stretch'):
                st.success("Data export started")
    
    with col3:
        with st.container():
            st.markdown("""
            <div class="glass-card">
                <h3>📱 Mobile App</h3>
                <p>Status: <span style="color: #00ff00;">✅ Connected</span></p>
                <p>Active Users: 8</p>
                <p>Push Notifications: Enabled</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Send Push", key="push_notif", width='stretch'):
                st.info("Notification sent to all mobile users")
    
    # API endpoints
    st.markdown("### 🔗 API Endpoints")
    api_data = pd.DataFrame({
        'Endpoint': ['/api/v1/inventory', '/api/v1/orders', '/api/v1/analytics', '/api/v1/users'],
        'Method': ['GET, POST', 'GET, PUT', 'GET', 'GET, POST, DELETE'],
        'Status': ['🟢 Active', '🟢 Active', '🟢 Active', '🟢 Active'],
        'Calls/min': ['245', '189', '567', '43']
    })
    st.dataframe(api_data, width='stretch', hide_index=True)

# Tab 7: Video Call
with tab7:
    st.markdown("### 📹 One-Click Video Conference")
    st.markdown("Start instant video meetings with your team")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🚀 Quick Start")
        
        # Room name input
        custom_room = st.text_input("Room Name (optional)", placeholder="Leave empty for auto-generated")
        
        if st.button("🎥 Start Video Conference", width='stretch'):
            if custom_room:
                room_id = custom_room.replace(" ", "-").lower()
            else:
                # Generate random room ID
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                room_id = f"WMS-{random_suffix}"
            
            st.session_state['current_room'] = room_id
            st.session_state['show_meeting_options'] = True
            st.rerun()
    
    with col2:
        st.markdown("#### 🎯 Active Meetings")
        if 'current_room' in st.session_state and st.session_state['current_room']:
            st.info(f"Current Room: **{st.session_state['current_room']}**")
        else:
            st.info("No active meeting")
        
        # Show team members
        st.markdown("#### 👥 Team Members")
        st.success("🟢 Salphine Chemos (Manager)")
        st.success("🟢 Kelvin Glance (Shipping)")
        st.success("🟢 Mike Kibet (Tech)")
        st.warning("🟡 Brendah Chepkoech (Break)")
    
    # Show meeting options if room is created
    if 'show_meeting_options' in st.session_state and st.session_state['show_meeting_options']:
        st.markdown("---")
        st.markdown("### 🎬 Choose Meeting Platform")
        
        call_option = st.radio(
            "Select platform:",
            ["Jitsi Meet (Open Source - Free)", "Google Meet", "Zoom", "Microsoft Teams"],
            horizontal=True
        )
        
        room_id = st.session_state.get('current_room', 'wms-meeting')
        
        if call_option == "Jitsi Meet (Open Source - Free)":
            jitsi_url = f"https://meet.jit.si/{room_id}"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; text-align: center;">
                <h4>🎥 Jitsi Meeting Ready!</h4>
                <p>Room: <b>{room_id}</b></p>
                <p>Click the link below to join:</p>
                <a href="{jitsi_url}" target="_blank" style="background-color: #ffd700; color: #1e3c72; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; margin: 15px 0;">🎥 Join Jitsi Meeting</a>
                <p style="margin-top: 10px; font-size: 14px;">✅ Works on mobile • No account needed • Free</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Copy room ID button
            st.code(f"Room ID: {room_id}", language="text")
            st.caption("Share this room ID with team members")
            
        elif call_option == "Google Meet":
            st.info("""
            **Google Meet Instructions:**
            1. Go to [meet.google.com](https://meet.google.com)
            2. Click 'Start a meeting'
            3. Share the meeting code with your team
            """)
            st.code(f"Suggested meeting name: {room_id}", language="text")
            
        elif call_option == "Zoom":
            st.info("""
            **Zoom Instructions:**
            1. Open Zoom app or go to [zoom.us](https://zoom.us)
            2. Click 'Host a meeting'
            3. Share the meeting ID with your team
            """)
            st.code(f"Suggested meeting ID: {room_id}", language="text")
            
        else:  # Microsoft Teams
            st.info("""
            **Microsoft Teams Instructions:**
            1. Open Microsoft Teams
            2. Click 'Meet now'
            3. Share the meeting link with your team
            """)
            st.code(f"Suggested meeting name: {room_id}", language="text")
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copy Room ID", width='stretch'):
                st.success(f"Copied: {room_id}")
        with col2:
            if st.button("🆕 New Room", width='stretch'):
                st.session_state['show_meeting_options'] = False
                if 'current_room' in st.session_state:
                    del st.session_state['current_room']
                st.rerun()
        with col3:
            if st.button("🎤 Test Mic/Camera", width='stretch'):
                st.info("Check your devices before joining")
    
    # Meeting tips
    with st.expander("💡 Meeting Tips"):
        st.markdown("""
        - **Jitsi Meet**: Free, no account needed, works in browser
        - **Google Meet**: Free with Google account
        - **Zoom**: Free for 40-min meetings
        - **Teams**: Free with Microsoft account
        - Test your camera/mic before joining
        - Share the room ID with team members
        - Use headphones to prevent echo
        """)

# Footer
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
footer_html = f'''
<div class="footer-container">
    <div class="footer-links">
        <a href="#" class="footer-link" target="_blank">📚 API Docs</a>
        <a href="#" class="footer-link" target="_blank">🆘 Support</a>
        <a href="#" class="footer-link" target="_blank">📧 Contact</a>
        <a href="#" class="footer-link" target="_blank">🔒 Privacy</a>
        <a href="#" class="footer-link" target="_blank">📜 Terms</a>
        <a href="#" class="footer-link" target="_blank">🤖 AI Help</a>
    </div>
    <div style="display: flex; justify-content: center; align-items: center; gap: 25px; margin: 8px 0;">
        <div style="display: flex; align-items: center;">
            <span class="status-indicator status-online"></span>
            <span style="font-size: 13px;">All Systems Operational</span>
        </div>
        <span class="metric-badge">⚡ Response: 0.3s</span>
        <span class="metric-badge">📈 Uptime: 99.9%</span>
        <span class="metric-badge">👥 Users: 23</span>
    </div>
    <div style="font-size: 11px; color: #ccc;">© 2026 Salphine chemos Smart WMS | {current_time}</div>
</div>
'''
st.markdown(footer_html, unsafe_allow_html=True)

# Update timestamp
if (datetime.now() - st.session_state.last_update).seconds >= refresh_rate:
    st.session_state.last_update = datetime.now()
    # Generate random sensor data for history
    st.session_state.sensor_history.append({
        'time': datetime.now(),
        'temperature': random.uniform(20, 30),
        'humidity': random.uniform(40, 80)
    })
    if len(st.session_state.sensor_history) > 100:
        st.session_state.sensor_history = st.session_state.sensor_history[-100:]
