"""
Advanced Real-Time Dashboard with Multiple Applications
Smart Warehouse Management System - Fixed Version
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
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(
    page_title="Smart WMS - Advanced Dashboard",
    page_icon="??",
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
    </style>
""", unsafe_allow_html=True)

# Initialize session states for real-time applications
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.login_attempts = 0
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

# Auto-refresh configuration
refresh_rate = st.sidebar.slider("?? Refresh Rate (seconds)", 1, 60, 5)
count = st_autorefresh(interval=refresh_rate * 1000, key="auto_refresh")

# Sidebar with real-time info
with st.sidebar:
    st.markdown("## ?? AI Control Center")
    
    # Real-time clock
    st.markdown(f"### ?? {datetime.now().strftime('%H:%M:%S')}")
    
    # User profile
    with st.expander("?? User Profile", expanded=True):
        st.markdown("**Logged in as:** Admin User")
        st.markdown(f"**Last login:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.progress(0.7, text="Profile Completion")
    
    # System health
    with st.expander("??? System Health", expanded=True):
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
    with st.expander("? Quick Actions", expanded=True):
        if st.button("?? Generate Report", use_container_width=True):
            st.session_state.notifications.append({
                'time': datetime.now(),
                'message': 'Report generation started',
                'type': 'info'
            })
        
        if st.button("?? Sync Data", use_container_width=True):
            with st.spinner("Syncing..."):
                time.sleep(2)
            st.success("Data synced!")
        
        if st.button("?? Send Alerts", use_container_width=True):
            st.info("Alerts sent to all users")
    
    # System performance metrics
    st.markdown("---")
    st.markdown("### ?? System Performance")
    
    # Real-time metrics
    metrics_col1, metrics_col2 = st.columns(2)
    with metrics_col1:
        st.metric("Response Time", "0.3s", "-0.1s")
        st.metric("CPU Load", "45%", "+5%")
    with metrics_col2:
        st.metric("Memory", "62%", "-2%")
        st.metric("Network", "1.2 MB/s", "+0.3")
    
    # Data stream indicator
    st.markdown("### ?? Data Stream")
    st.progress(random.uniform(0.5, 0.9), text=f"Live Data: {random.randint(100, 500)} packets/s")

# Main header
current_time = datetime.now().strftime('%H:%M:%S')
st.markdown(f"""
<div class="main-header">
    <h1>?? Advanced Smart WMS Dashboard</h1>
    <p style="font-size: 1.2rem;">Real-time warehouse management with AI-powered insights and automation</p>
    <div style="display: flex; gap: 20px; margin-top: 20px;">
        <span>?? Live</span>
        <span>?? Real-time Analytics</span>
        <span>?? AI Assistant</span>
        <span>? Auto-refresh: {refresh_rate}s</span>
    </div>
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

# Create tabs for different real-time applications
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "?? Live Analytics",
    "?? AI Assistant",
    "?? Team Chat",
    "?? Task Manager",
    "?? Predictions",
    "?? Integrations"
])

# Tab 1: Live Analytics
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ?? Real-time Sensor Data")
        
        # Simulate real-time data
        current_time = datetime.now()
        new_data = pd.DataFrame({
            'timestamp': [current_time],
            'value': [random.uniform(50, 150)],
            'category': [random.choice(['Temperature', 'Humidity', 'Pressure', 'Vibration'])]
        })
        
        st.session_state.real_time_data = pd.concat([st.session_state.real_time_data, new_data], ignore_index=True)
        if len(st.session_state.real_time_data) > 50:
            st.session_state.real_time_data = st.session_state.real_time_data.tail(50)
        
        # Live line chart
        fig_live = go.Figure()
        for category in st.session_state.real_time_data['category'].unique():
            cat_data = st.session_state.real_time_data[st.session_state.real_time_data['category'] == category]
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
        st.plotly_chart(fig_live, use_container_width=True)
    
    with col2:
        st.markdown("### ?? Live Metrics")
        
        # Real-time gauges
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Temperature gauge
            temp = random.uniform(20, 30)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=temp,
                title={'text': "Temperature C"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [None, 50]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 20], 'color': "lightgray"},
                           {'range': [20, 30], 'color': "gray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 40}}))
            fig_gauge.update_layout(height=250)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col_b:
            # Humidity gauge
            humidity = random.uniform(40, 80)
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
            fig_gauge2.update_layout(height=250)
            st.plotly_chart(fig_gauge2, use_container_width=True)
        
        # Live alerts
        st.markdown("### ?? Live Alerts")
        alert_container = st.container()
        with alert_container:
            if random.random() > 0.7:
                st.error(f"?? High temperature detected in Zone A at {datetime.now().strftime('%H:%M:%S')}")
            if random.random() > 0.8:
                st.warning(f"?? Low inventory alert: SKU-{random.randint(100,999)}")
            if random.random() > 0.9:
                st.success(f"? System optimized at {datetime.now().strftime('%H:%M:%S')}")

# Tab 2: AI Assistant
with tab2:
    st.markdown("### ?? AI Warehouse Assistant")
    st.markdown("Ask me anything about your warehouse operations")
    
    # Chat interface
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat messages
        if not st.session_state.chat_messages:
            st.markdown('<div class="message bot-message">?? Hello! How can I help you with your warehouse today?</div>', unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_messages[-10:]:
                if msg['type'] == 'user':
                    st.markdown(f'<div class="message user-message">?? {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="message bot-message">?? {msg["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Type your message:", key="ai_input")
    with col2:
        if st.button("Send", use_container_width=True):
            if user_input:
                st.session_state.chat_messages.append({'type': 'user', 'content': user_input})
                
                # Simple AI responses
                responses = {
                    'inventory': "Current inventory level is 78% of capacity. Low stock items: SKU-123, SKU-456",
                    'order': "There are 23 pending orders. 5 are high priority.",
                    'temperature': "Temperature is normal across all zones. Zone B is showing slight variation.",
                    'performance': "System performance is optimal. Response time: 0.3s",
                    'forecast': "Based on current trends, expect 15% increase in orders tomorrow."
                }
                
                response = responses.get(random.choice(list(responses.keys())), 
                                        "I'm analyzing your request. The system is processing...")
                st.session_state.chat_messages.append({'type': 'bot', 'content': response})
                st.rerun()
    
    # AI suggestions
    with st.expander("?? AI Suggestions", expanded=True):
        st.info("?? Consider restocking SKU-123 - below threshold")
        st.info("? Peak order time detected - allocate more resources")
        st.info("?? Maintenance recommended for Conveyor Belt B in 2 hours")

# Tab 3: Team Chat
with tab3:
    st.markdown("### ?? Team Communication")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Team chat
        st.markdown("#### Live Team Chat")
        
        # Chat messages
        team_chat = st.container()
        with team_chat:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">????? John: Inventory check completed</div>', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">????? Sarah: Shipping department ready</div>', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">????? Mike: Maintenance scheduled for 3 PM</div>', unsafe_allow_html=True)
            st.markdown('<div class="message bot-message">?? System: New order received #ORD-789</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Message input
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.text_input("Type your message...", key="team_msg")
        with col_b:
            st.button("?? Send", key="send_team")
    
    with col2:
        st.markdown("#### Team Online")
        st.success("?? John (Manager)")
        st.success("?? Sarah (Shipping)")
        st.success("?? Mike (Tech)")
        st.warning("?? Alice (Break)")
        st.error("?? Bob (Offline)")
        
        st.markdown("#### Quick Actions")
        if st.button("?? Start Video Call"):
            st.info("Video call feature coming soon!")
        if st.button("?? Broadcast Message"):
            st.info("Broadcast sent to all team members")

# Tab 4: Task Manager
with tab4:
    st.markdown("### ?? Real-time Task Management")
    
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
            use_container_width=True,
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
        fig_tasks = px.bar(
            tasks_data,
            x='Task ID',
            y='Progress',
            color='Priority',
            title="Task Completion Progress"
        )
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

# Tab 5: Predictions
with tab5:
    st.markdown("### ?? AI-Powered Predictions")
    
    # Prediction charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Demand forecast
        future_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        demand_forecast = pd.DataFrame({
            'Date': future_dates,
            'Predicted Demand': [random.uniform(80, 120) + i*0.5 for i in range(30)],
            'Upper Bound': [random.uniform(90, 130) + i*0.5 for i in range(30)],
            'Lower Bound': [random.uniform(70, 110) + i*0.5 for i in range(30)]
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
            line=dict(dash='dash', color='gray')
        ))
        fig_forecast.add_trace(go.Scatter(
            x=demand_forecast['Date'],
            y=demand_forecast['Lower Bound'],
            mode='lines',
            name='Lower Bound',
            line=dict(dash='dash', color='gray'),
            fill='tonexty'
        ))
        
        fig_forecast.update_layout(title="30-Day Demand Forecast", height=400)
        st.plotly_chart(fig_forecast, use_container_width=True)
    
    with col2:
        # Inventory prediction
        categories = ['Electronics', 'Clothing', 'Food', 'Furniture', 'Tools']
        current_inv = [random.uniform(60, 100) for _ in categories]
        predicted_inv = [x * random.uniform(0.8, 1.2) for x in current_inv]
        
        fig_inv_pred = go.Figure(data=[
            go.Bar(name='Current', x=categories, y=current_inv),
            go.Bar(name='Predicted (30 days)', x=categories, y=predicted_inv)
        ])
        fig_inv_pred.update_layout(title="Inventory Level Prediction", height=400, barmode='group')
        st.plotly_chart(fig_inv_pred, use_container_width=True)
    
    # AI Insights
    st.markdown("### ?? AI Insights")
    insight_cols = st.columns(3)
    
    with insight_cols[0]:
        st.info("?? **Trend**: 15% increase in orders expected next week")
    with insight_cols[1]:
        st.warning("?? **Risk**: Potential stockout for Electronics category")
    with insight_cols[2]:
        st.success("?? **Opportunity**: Optimize shipping routes for 20% savings")

# Tab 6: Integrations
with tab6:
    st.markdown("### ?? System Integrations")
    
    # Integration cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="glass-card">
                <h3>?? ERP System</h3>
                <p>Status: <span style="color: #00ff00;">Connected</span></p>
                <p>Last Sync: 2 minutes ago</p>
                <p>Data Flow: 1.2 MB/s</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Sync Now", key="sync_erp"):
                st.success("ERP sync initiated")
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="glass-card">
                <h3>?? BI Tools</h3>
                <p>Status: <span style="color: #00ff00;">Connected</span></p>
                <p>Last Export: 5 minutes ago</p>
                <p>Reports: 12 generated today</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Export Data", key="export_bi"):
                st.success("Data export started")
    
    with col3:
        with st.container():
            st.markdown("""
            <div class="glass-card">
                <h3>?? Mobile App</h3>
                <p>Status: <span style="color: #00ff00;">Connected</span></p>
                <p>Active Users: 8</p>
                <p>Push Notifications: Enabled</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Send Push", key="push_notif"):
                st.info("Notification sent to all mobile users")
    
    # API endpoints
    st.markdown("### ?? API Endpoints")
    api_data = pd.DataFrame({
        'Endpoint': ['/api/v1/inventory', '/api/v1/orders', '/api/v1/analytics', '/api/v1/users'],
        'Method': ['GET, POST', 'GET, PUT', 'GET', 'GET, POST, DELETE'],
        'Status': ['? Active', '? Active', '? Active', '? Active'],
        'Calls/min': ['245', '189', '567', '43']
    })
    st.dataframe(api_data, use_container_width=True, hide_index=True)

# Fixed Footer
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
footer_html = f'''
<div class="footer-container">
    <div class="footer-links">
        <a href="#" class="footer-link" target="_blank">?? API Docs</a>
        <a href="#" class="footer-link" target="_blank">?? Support</a>
        <a href="#" class="footer-link" target="_blank">?? Contact</a>
        <a href="#" class="footer-link" target="_blank">?? Privacy</a>
        <a href="#" class="footer-link" target="_blank">?? Terms</a>
        <a href="#" class="footer-link" target="_blank">?? AI Help</a>
    </div>
    <div style="display: flex; justify-content: center; align-items: center; gap: 25px; margin: 8px 0;">
        <div style="display: flex; align-items: center;">
            <span class="status-indicator"></span>
            <span style="font-size: 13px;">All Systems Operational</span>
        </div>
        <span class="metric-badge">? Response: 0.3s</span>
        <span class="metric-badge">?? Uptime: 99.9%</span>
        <span class="metric-badge">?? Users: 23</span>
    </div>
    <div style="font-size: 11px; color: #ccc;"> 2026 Smart WMS | {current_time}</div>
</div>
'''
st.markdown(footer_html, unsafe_allow_html=True)

# Update timestamp
if (datetime.now() - st.session_state.last_update).seconds >= refresh_rate:
    st.session_state.last_update = datetime.now()
    # Trigger any real-time updates here
    pass
