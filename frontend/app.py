import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import os

st.set_page_config(page_title="Smart WMS", page_icon="🏭", layout="wide")

# Get API URL from environment variable
API_URL = os.getenv("API_URL", "https://your-backend-url.onrender.com")

st.title("🏭 Smart Warehouse Management System")

try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    if response.status_code == 200:
        st.success("✅ Connected to backend")
        
        # Fetch inventory
        inv = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        if inv.status_code == 200:
            data = inv.json()
            df = pd.DataFrame(data)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total Products", len(df))
            with col2: st.metric("Total Items", int(df['current_quantity'].sum()))
            with col3: 
                low = len(df[df['needs_reorder'] == True])
                st.metric("Low Stock", low)
            with col4: st.metric("Healthy", len(df) - low)
            
            fig = px.bar(df, x='name', y='current_quantity', 
                        color='needs_reorder',
                        color_discrete_map={True: 'red', False: 'green'})
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df[['sku', 'name', 'current_quantity', 'reorder_point']])
    else:
        st.error("❌ Backend connection failed")
except Exception as e:
    st.error(f"Error: {e}")
    # Demo data
    df_demo = pd.DataFrame({
        'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
        'Stock': [2, 2, 1, 1]
    })
    st.dataframe(df_demo)

st.caption(f"Smart WMS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
