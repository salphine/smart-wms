import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random
from streamlit_autorefresh import st_autorefresh
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Advanced Real-Time Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Metric cards styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        text-align: center;
        padding: 1rem;
        font-size: 14px;
        z-index: 1000;
    }
    
    .footer a {
        color: #ffd700;
        text-decoration: none;
        margin: 0 15px;
        transition: color 0.3s ease;
    }
    
    .footer a:hover {
        color: #ffffff;
        text-decoration: underline;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    
    .status-online {
        background-color: #00ff00;
        box-shadow: 0 0 10px #00ff00;
    }
    
    /* Chart container */
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        transition: transform 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for real-time data
if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=['timestamp', 'value1', 'value2', 'value3', 'category'])

if 'alert_count' not in st.session_state:
    st.session_state.alert_count = 0

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Auto-refresh configuration
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", min_value=1, max_value=60, value=5)
count = st_autorefresh(interval=refresh_interval * 1000, key="auto_refresh")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=DASHBOARD+LOGO", use_container_width=True)
    
    st.markdown("## ⚙️ Dashboard Controls")
    
    # Real-time data simulation controls
    st.markdown("### Data Simulation")
    data_rate = st.slider("Data Generation Rate", min_value=1, max_value=20, value=5)
    volatility = st.slider("Volatility", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
    
    # Alert threshold
    alert_threshold = st.number_input("Alert Threshold", min_value=0, max_value=100, value=80)
    
    # Theme selector
    theme = st.selectbox("Theme", ["Light", "Dark", "System"])
    
    st.markdown("---")
    
    # Status indicators
    st.markdown("### System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="status-indicator status-online"></span> Database', unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="status-indicator status-online"></span> API', unsafe_allow_html=True)
    
    # Manual refresh button
    if st.button("🔄 Refresh Data Now"):
        st.rerun()
    
    st.markdown("---")
    st.markdown(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Main content
st.title("📊 Advanced Real-Time Dashboard")
st.markdown("### Monitor your metrics in real-time with live updates")

# Generate real-time data
def generate_real_time_data():
    new_data = pd.DataFrame({
        'timestamp': [datetime.now()],
        'value1': [50 + np.random.randn() * 10 * volatility],
        'value2': [75 + np.random.randn() * 15 * volatility],
        'value3': [30 + np.random.randn() * 5 * volatility],
        'category': [random.choice(['A', 'B', 'C', 'D'])]
    })
    
    # Append to history and keep last 100 records
    st.session_state.data_history = pd.concat([st.session_state.data_history, new_data], ignore_index=True)
    if len(st.session_state.data_history) > 100:
        st.session_state.data_history = st.session_state.data_history.tail(100)
    
    # Update alert count
    if new_data['value1'].iloc[0] > alert_threshold:
        st.session_state.alert_count += 1
    
    st.session_state.last_update = datetime.now()
    return new_data

# Generate new data
new_data = generate_real_time_data()

# KPI Metrics Row
st.markdown("### Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Current Value 1</h3>
        <h2>{new_data['value1'].iloc[0]:.1f}</h2>
        <p>⬆️ +{abs(np.random.randn()*2):.1f}% from average</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <h3>Current Value 2</h3>
        <h2>{new_data['value2'].iloc[0]:.1f}</h2>
        <p>⬇️ -{abs(np.random.randn()*1.5):.1f}% from average</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <h3>Current Value 3</h3>
        <h2>{new_data['value3'].iloc[0]:.1f}</h2>
        <p>📊 Stable trend</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
        <h3>Active Alerts</h3>
        <h2>{st.session_state.alert_count}</h2>
        <p>⚠️ Threshold: {alert_threshold}</p>
    </div>
    """, unsafe_allow_html=True)

# Charts Row
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📈 Real-Time Trends")
    
    # Line chart with Plotly
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=st.session_state.data_history['timestamp'],
        y=st.session_state.data_history['value1'],
        mode='lines+markers',
        name='Value 1',
        line=dict(color='#667eea', width=3)
    ))
    fig_line.add_trace(go.Scatter(
        x=st.session_state.data_history['timestamp'],
        y=st.session_state.data_history['value2'],
        mode='lines+markers',
        name='Value 2',
        line=dict(color='#f093fb', width=3)
    ))
    fig_line.update_layout(
        title="Live Data Stream",
        xaxis_title="Time",
        yaxis_title="Values",
        hovermode='x unified',
        template="plotly_white"
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📊 Distribution Analysis")
    
    # Histogram
    fig_hist = px.histogram(
        st.session_state.data_history, 
        x='value1',
        nbins=20,
        title="Value Distribution",
        color_discrete_sequence=['#667eea']
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Second row of charts
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 🎯 Category Distribution")
    
    # Pie chart
    category_counts = st.session_state.data_history['category'].value_counts()
    fig_pie = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Data by Category"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📉 Moving Averages")
    
    # Moving average
    if len(st.session_state.data_history) > 10:
        st.session_state.data_history['MA5'] = st.session_state.data_history['value1'].rolling(window=5).mean()
        st.session_state.data_history['MA10'] = st.session_state.data_history['value1'].rolling(window=10).mean()
        
        fig_ma = go.Figure()
        fig_ma.add_trace(go.Scatter(
            x=st.session_state.data_history['timestamp'],
            y=st.session_state.data_history['value1'],
            name='Actual',
            line=dict(color='gray', width=1)
        ))
        fig_ma.add_trace(go.Scatter(
            x=st.session_state.data_history['timestamp'],
            y=st.session_state.data_history['MA5'],
            name='5-period MA',
            line=dict(color='red', width=2)
        ))
        fig_ma.add_trace(go.Scatter(
            x=st.session_state.data_history['timestamp'],
            y=st.session_state.data_history['MA10'],
            name='10-period MA',
            line=dict(color='blue', width=2)
        ))
        st.plotly_chart(fig_ma, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Data Table
st.markdown("### 📋 Recent Data")
st.dataframe(
    st.session_state.data_history.tail(10),
    use_container_width=True,
    hide_index=True
)

# Export functionality
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("📥 Export to CSV"):
        csv = st.session_state.data_history.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📊 Generate Report"):
        st.success("Report generated successfully!")

# Footer with important links
st.markdown("""
<div class="footer">
    <div style="margin-bottom: 10px;">
        <strong>Important Links:</strong>
    </div>
    <div>
        <a href="#" target="_blank">📊 Dashboard Home</a>
        <a href="#" target="_blank">📈 Analytics</a>
        <a href="#" target="_blank">⚙️ Settings</a>
        <a href="#" target="_blank">📄 Documentation</a>
        <a href="#" target="_blank">🆘 Support</a>
        <a href="#" target="_blank">📧 Contact</a>
        <a href="#" target="_blank">📱 API Status</a>
        <a href="#" target="_blank">🔒 Privacy Policy</a>
    </div>
    <div style="margin-top: 10px; font-size: 12px; color: #cccccc;">
        © 2025 Advanced Dashboard | Version 2.0 | Real-time updates every {} seconds
    </div>
</div>
""".format(refresh_interval), unsafe_allow_html=True)

# Alert notifications
if new_data['value1'].iloc[0] > alert_threshold:
    st.toast(f"⚠️ Alert: Value 1 exceeded {alert_threshold}!", icon="⚠️")
    st.sidebar.error(f"Alert triggered at {datetime.now().strftime('%H:%M:%S')}")

# Performance metrics
st.sidebar.markdown("---")
st.sidebar.markdown("### Performance Metrics")
st.sidebar.metric("Data Points", len(st.session_state.data_history))
st.sidebar.metric("Refresh Rate", f"{refresh_interval}s")
st.sidebar.metric("Uptime", "99.9%")

# Real-time clock
st.sidebar.markdown("---")
st.sidebar.markdown(f"### 🕐 Server Time")
st.sidebar.markdown(f"**{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")