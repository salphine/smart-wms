import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Scan Diagnostics", layout="wide")
st.title("🔍 Scan Data Diagnostic Tool")

API_URL = "http://localhost:8000"

# Check backend connection
st.subheader("1. Backend Connection Check")
try:
    health = requests.get(f"{API_URL}/health", timeout=5)
    if health.status_code == 200:
        st.success(f"✅ Backend Connected: {health.json()}")
    else:
        st.error(f"❌ Backend Error: {health.status_code}")
except Exception as e:
    st.error(f"❌ Cannot connect to backend: {e}")
    st.stop()

# Fetch scan data directly
st.subheader("2. Raw Scan Data from API")

try:
    response = requests.get(f"{API_URL}/api/scans/recent?limit=50", timeout=5)
    if response.status_code == 200:
        scan_data = response.json()
        st.write(f"**Found {len(scan_data)} scans**")
        
        if scan_data:
            st.json(scan_data[:3])  # Show first 3 scans as example
            
            # Convert to DataFrame
            df = pd.DataFrame(scan_data)
            st.write("**DataFrame Info:**")
            st.write(f"Shape: {df.shape}")
            st.write(f"Columns: {df.columns.tolist()}")
            
            # Check each column
            st.subheader("3. Column Analysis")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'rfid_tag' in df.columns:
                    st.success(f"✅ rfid_tag column exists")
                    st.write(f"Sample: {df['rfid_tag'].iloc[0] if len(df) > 0 else 'No data'}")
                else:
                    st.error("❌ rfid_tag column missing")
            
            with col2:
                if 'created_at' in df.columns:
                    st.success(f"✅ created_at column exists")
                    # Try to convert to datetime
                    try:
                        pd.to_datetime(df['created_at'])
                        st.write("✅ Can convert to datetime")
                    except:
                        st.error("❌ Cannot convert to datetime")
                else:
                    st.error("❌ created_at column missing")
            
            with col3:
                if 'location' in df.columns:
                    st.success(f"✅ location column exists")
                else:
                    st.error("❌ location column missing")
            
            # Show the data
            st.subheader("4. Scan Data Table")
            if not df.empty:
                # Try to format datetime if it exists
                if 'created_at' in df.columns:
                    try:
                        df['formatted_time'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        display_cols = ['rfid_tag', 'action', 'location', 'scanned_by', 'formatted_time']
                        # Only include columns that exist
                        display_cols = [col for col in display_cols if col in df.columns]
                        st.dataframe(df[display_cols].head(10), use_container_width=True)
                    except:
                        st.dataframe(df.head(10), use_container_width=True)
                else:
                    st.dataframe(df.head(10), use_container_width=True)
            else:
                st.warning("DataFrame is empty")
        else:
            st.warning("No scan data returned from API")
    else:
        st.error(f"API Error: {response.status_code}")
except Exception as e:
    st.error(f"Error fetching scans: {e}")

# Check transactions table directly in database
st.subheader("5. Direct Database Check")

try:
    import sqlite3
    import os
    
    db_path = os.path.join("..", "backend", "wms.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if transactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if cursor.fetchone():
            st.success("✅ Transactions table exists")
            
            # Count rows
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            st.write(f"**Rows in transactions table: {count}**")
            
            if count > 0:
                # Show sample data
                cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute("PRAGMA table_info(transactions)")
                columns = [col[1] for col in cursor.fetchall()]
                
                df_db = pd.DataFrame(rows, columns=columns)
                st.dataframe(df_db)
            else:
                st.warning("Transactions table is empty")
        else:
            st.error("❌ Transactions table does not exist")
        
        conn.close()
    else:
        st.error(f"Database file not found at {db_path}")
except Exception as e:
    st.error(f"Error checking database: {e}")

# Manual scan addition test
st.subheader("6. Add Test Scan")

col_a, col_b = st.columns(2)
with col_a:
    rfid_tag = st.text_input("RFID Tag", "RFID001")
    location = st.text_input("Location", "Test Location")
with col_b:
    scanner_id = st.text_input("Scanner ID", "diagnostic")
    if st.button("Add Test Scan"):
        try:
            payload = {
                "rfid_tag": rfid_tag,
                "location": location,
                "scanner_id": scanner_id
            }
            response = requests.post(f"{API_URL}/api/scans/", json=payload)
            if response.status_code == 200:
                st.success(f"✅ Scan added: {response.json()}")
                st.cache_data.clear()
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

# Recommendations
st.subheader("7. Recommendations")

if 'scan_data' in locals() and scan_data:
    if len(scan_data) == 0:
        st.warning("⚠️ No scans found. Add some scans using the form above.")
    else:
        if 'created_at' in df.columns:
            try:
                df['created_at'] = pd.to_datetime(df['created_at'])
                st.success("✅ Scans are available and properly formatted")
            except:
                st.error("❌ created_at column needs formatting")
        else:
            st.error("❌ Missing created_at column - check API response")
else:
    st.info("Add some scans to see them in the dashboard")
