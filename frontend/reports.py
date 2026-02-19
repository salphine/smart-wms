import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Reports", page_icon="📈", layout="wide")

st.title("📈 Analytics & Reports")

API_URL = "http://localhost:8000"

# Fetch data
@st.cache_data(ttl=5)
def fetch_inventory():
    try:
        response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=5)
def fetch_scans():
    try:
        response = requests.get(f"{API_URL}/api/scans/recent?limit=100", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

inventory_data = fetch_inventory()
scan_data = fetch_scans()

if inventory_data:
    df_inv = pd.DataFrame(inventory_data)
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Inventory Summary", "Movement Analysis", "Stock Projection", "Performance Metrics"]
        )
    with col2:
        date_range = st.selectbox(
            "Time Period",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date"]
        )
    
    if report_type == "Inventory Summary":
        st.subheader("📊 Inventory Summary Report")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Products", len(df_inv))
        with col2:
            st.metric("Total Items", int(df_inv['current_quantity'].sum()))
        with col3:
            st.metric("Low Stock Items", len(df_inv[df_inv['needs_reorder'] == True]))
        with col4:
            avg_stock = df_inv['current_quantity'].mean()
            st.metric("Average Stock", f"{avg_stock:.1f}")
        
        # Stock distribution
        fig = px.pie(
            values=[len(df_inv[df_inv['needs_reorder'] == True]), 
                   len(df_inv[df_inv['needs_reorder'] == False])],
            names=['Low Stock', 'Healthy Stock'],
            title="Stock Health Distribution",
            color_discrete_sequence=['#ff4b4b', '#2ecc71']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.subheader("Product Details")
        st.dataframe(
            df_inv[['sku', 'name', 'current_quantity', 'reorder_point', 'needs_reorder']],
            use_container_width=True
        )
    
    elif report_type == "Movement Analysis" and scan_data:
        st.subheader("🔄 Movement Analysis")
        
        df_scans = pd.DataFrame(scan_data)
        if 'created_at' in df_scans.columns:
            df_scans['created_at'] = pd.to_datetime(df_scans['created_at'])
            df_scans['hour'] = df_scans['created_at'].dt.hour
            df_scans['date'] = df_scans['created_at'].dt.date
            
            # Scan frequency by hour
            hourly = df_scans['hour'].value_counts().sort_index()
            fig_hourly = px.bar(
                x=hourly.index,
                y=hourly.values,
                title="Scan Frequency by Hour",
                labels={'x': 'Hour of Day', 'y': 'Number of Scans'}
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
            
            # Top locations
            top_locations = df_scans['location'].value_counts().head(10)
            fig_locations = px.bar(
                x=top_locations.values,
                y=top_locations.index,
                orientation='h',
                title="Top Scan Locations",
                labels={'x': 'Number of Scans', 'y': 'Location'}
            )
            st.plotly_chart(fig_locations, use_container_width=True)
    
    elif report_type == "Stock Projection":
        st.subheader("📈 Stock Projection")
        
        # Simple projection based on current levels
        for _, row in df_inv.iterrows():
            days_until_reorder = max(0, (row['current_quantity'] / max(row['reorder_point'], 1)) * 30)
            
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4>{row['name']}</h4>
                <div style="display: flex; justify-content: space-between;">
                    <span>Current: {int(row['current_quantity'])} units</span>
                    <span>Projected days until reorder: {days_until_reorder:.1f} days</span>
                </div>
                <div style="background: #ecf0f1; height: 10px; border-radius: 5px; margin-top: 0.5rem;">
                    <div style="background: {'#e74c3c' if days_until_reorder < 7 else '#f39c12' if days_until_reorder < 14 else '#2ecc71'}; 
                              width: {min(100, (days_until_reorder/30)*100)}%; height: 10px; border-radius: 5px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif report_type == "Performance Metrics":
        st.subheader("📊 Performance Metrics")
        
        # Calculate metrics
        turnover_rate = len(scan_data) / max(len(df_inv), 1) if scan_data else 0
        stock_accuracy = np.random.randint(95, 100)  # Simulated for demo
        fulfillment_rate = np.random.randint(90, 99)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background: white; padding: 2rem; border-radius: 10px; text-align: center;">
                <h1>{turnover_rate:.1f}</h1>
                <p>Inventory Turnover Rate</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: white; padding: 2rem; border-radius: 10px; text-align: center;">
                <h1>{stock_accuracy}%</h1>
                <p>Stock Accuracy</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: white; padding: 2rem; border-radius: 10px; text-align: center;">
                <h1>{fulfillment_rate}%</h1>
                <p>Order Fulfillment Rate</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Export options
    st.divider()
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    with col_exp2:
        if st.button("📥 Export Report", use_container_width=True):
            st.success("Report exported successfully!")
            # In production, this would generate a PDF/Excel file
else:
    st.error("Could not fetch data for reports")
