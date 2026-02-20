
# ===== ADDED: Video Call Feature =====
try:
    # Add new tab for video calls
    if 'tab7' not in locals():
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Live Analytics", "🤖 AI Assistant", "💬 Team Chat",
            "📋 Task Manager", "📈 Predictions", "🔌 Integrations", "📹 Video Call"
        ])
    
    with tab7:
        st.markdown("### 📹 One-Click Video Conference")
        
        import random
        import string
        
        col1, col2 = st.columns(2)
        
        with col1:
            room_name = st.text_input("Room name", placeholder="Enter room name")
            if st.button("🎥 Start Meeting", use_container_width=True):
                room_id = room_name if room_name else f"WMS-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
                jitsi_url = f"https://meet.jit.si/{room_id}"
                st.markdown(f'<a href="{jitsi_url}" target="_blank" style="background-color: #28a745; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-size: 18px;">🔗 Join Video Call</a>', unsafe_allow_html=True)
                st.info(f"Room ID: {room_id}")
        
        with col2:
            st.markdown("#### 📋 How to use:")
            st.markdown("1. Enter room name or leave empty for random")
            st.markdown("2. Click 'Start Meeting'")
            st.markdown("3. Share the room ID with team")
            st.markdown("4. Click the green button to join")
            
        st.caption("Powered by Jitsi Meet - Free, no account needed")
except Exception as e:
    st.warning(f"Video call feature could not be loaded: {e}")
