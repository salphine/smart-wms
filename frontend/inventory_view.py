import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(page_title="Inventory View", page_icon="📦", layout="wide")

st.title("📦 Detailed Inventory View")

API_URL = "http://localhost:8000"

# Fetch inventory data
@st.cache_data(ttl=5)
def fetch_inventory():
    try:
        response = requests.get(f"{API_URL}/api/inventory/levels", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

data = fetch_inventory()

if data:
    df = pd.DataFrame(data)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search Product")
    with col2:
        status_filter = st.selectbox("Status", ["All", "Low Stock", "Healthy"])
    with col3:
        sort_by = st.selectbox("Sort By", ["Name", "Stock Level", "Reorder Point"])
    
    # Apply filters
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search, case=False)]
    if status_filter == "Low Stock":
        filtered_df = filtered_df[filtered_df['needs_reorder'] == True]
    elif status_filter == "Healthy":
        filtered_df = filtered_df[filtered_df['needs_reorder'] == False]
    
    # Display table
    st.dataframe(
        filtered_df[['sku', 'name', 'current_quantity', 'reorder_point', 'reorder_quantity', 'needs_reorder']],
        use_container_width=True,
        column_config={
            "sku": "SKU",
            "name": "Product",
            "current_quantity": "Current Stock",
            "reorder_point": "Reorder At",
            "reorder_quantity": "Reorder Qty",
            "needs_reorder": "Needs Reorder"
        }
    )
    
    # Export button
    if st.button("📥 Export to CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
else:
    st.error("Could not fetch inventory data")
