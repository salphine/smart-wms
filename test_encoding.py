import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Test", page_icon="✅")

st.title("Test Dashboard")
st.write("If you see emojis below, encoding is working:")

# Test emojis
st.write("📄 API Docs")
st.write("🆘 Support")
st.write("📧 Contact")
st.write("🔒 Privacy")
st.write("📜 Terms")
st.write("🤖 AI Help")
st.write("⚡ Response: 0.3s")
st.write("📈 Uptime: 99.9%")
st.write("👥 Users: 23")

st.markdown("---")
st.write(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
