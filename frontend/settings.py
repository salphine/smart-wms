import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ System Settings")

# Initialize session state for settings
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'refresh_interval': 10,
        'dark_mode': False,
        'notifications': True,
        'default_view': 'dashboard',
        'alert_threshold': 1.5,
        'backup_enabled': False
    }

tab1, tab2, tab3 = st.tabs(["General", "Notifications", "Advanced"])

with tab1:
    st.subheader("General Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.settings['refresh_interval'] = st.slider(
            "Default Refresh Interval (seconds)",
            min_value=5,
            max_value=60,
            value=st.session_state.settings['refresh_interval']
        )
        
        st.session_state.settings['default_view'] = st.selectbox(
            "Default Landing Page",
            ["dashboard", "inventory", "scans", "analytics"]
        )
    
    with col2:
        st.session_state.settings['dark_mode'] = st.toggle(
            "Dark Mode",
            value=st.session_state.settings['dark_mode']
        )
        
        st.session_state.settings['alert_threshold'] = st.slider(
            "Alert Threshold Multiplier",
            min_value=1.0,
            max_value=3.0,
            value=st.session_state.settings['alert_threshold'],
            step=0.1,
            help="Alert when stock falls below (reorder_point × multiplier)"
        )

with tab2:
    st.subheader("Notification Settings")
    
    st.session_state.settings['notifications'] = st.toggle(
        "Enable Notifications",
        value=st.session_state.settings['notifications']
    )
    
    if st.session_state.settings['notifications']:
        st.multiselect(
            "Notify for",
            ["Low Stock", "Critical Stock", "New Scans", "System Updates"],
            default=["Low Stock", "Critical Stock"]
        )
        
        st.text_input("Email for notifications", placeholder="admin@example.com")

with tab3:
    st.subheader("Advanced Settings")
    
    st.session_state.settings['backup_enabled'] = st.toggle(
        "Auto Backup",
        value=st.session_state.settings['backup_enabled']
    )
    
    if st.session_state.settings['backup_enabled']:
        st.selectbox("Backup Frequency", ["Hourly", "Daily", "Weekly"])
    
    st.divider()
    
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        st.session_state.settings = {
            'refresh_interval': 10,
            'dark_mode': False,
            'notifications': True,
            'default_view': 'dashboard',
            'alert_threshold': 1.5,
            'backup_enabled': False
        }
        st.success("Settings reset to defaults!")
        st.rerun()

# Save button
st.divider()
col_save1, col_save2, col_save3 = st.columns([1, 1, 1])
with col_save2:
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("Settings saved successfully!")
        
        # Here you would save to a config file or database
        with open('settings.json', 'w') as f:
            json.dump(st.session_state.settings, f)

# Display current settings
with st.expander("Current Settings (JSON)"):
    st.json(st.session_state.settings)
