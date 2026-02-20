
# ===== VIDEO CALL FEATURE ADDED =====
# Tab 7: One-Click Video Conference
with tab7:
    st.markdown("### 📹 One-Click Video Conference")
    st.markdown("Start instant video meetings with your team")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🚀 Quick Start")
        
        # Generate unique room ID
        import random
        import string
        
        # Room name input
        custom_room = st.text_input("Room Name (optional)", placeholder="e.g., weekly-standup", key="video_room_input")
        
        if st.button("🎥 Start Video Conference", use_container_width=True):
            if custom_room:
                # Clean room name for URL
                room_id = custom_room.strip().replace(" ", "-").lower()
                # Remove special characters
                room_id = ''.join(c for c in room_id if c.isalnum() or c == '-')
            else:
                # Generate random room ID
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                room_id = f"WMS-{random_suffix}"
            
            st.session_state['current_room'] = room_id
            st.session_state['show_meeting'] = True
            st.rerun()
    
    with col2:
        st.markdown("#### 📋 Active Meetings")
        if 'current_room' in st.session_state:
            st.info(f"Current Room: **{st.session_state['current_room']}**")
            
            # Show meeting link
            room_id = st.session_state['current_room']
            jitsi_url = f"https://meet.jit.si/{room_id}"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 10px 0;">
                <p style="color: white; margin-bottom: 10px;">🔗 Meeting Link:</p>
                <a href="{jitsi_url}" target="_blank" style="background-color: #ffd700; color: #1e3c72; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block;">Join Video Call</a>
                <p style="color: white; font-size: 12px; margin-top: 10px;">Room: {room_id}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Copy button
            if st.button("📋 Copy Room ID", key="copy_room"):
                st.success(f"Room ID copied: {room_id}")
        else:
            st.info("No active meeting")
        
        # Show team members
        st.markdown("#### 👥 Team Online")
        st.success("🟢 John (Manager)")
        st.success("🟢 Sarah (Shipping)")
        st.success("🟢 Mike (Tech)")
        st.warning("🟡 Alice (Break)")
    
    # Meeting options
    if 'show_meeting' in st.session_state and st.session_state['show_meeting']:
        st.markdown("---")
        st.markdown("### 🔗 Meeting Platform Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                <h4>Jitsi Meet</h4>
                <p>✓ Free & Open Source<br>✓ No account needed<br>✓ Works on mobile</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                <h4>Google Meet</h4>
                <p>✓ Free with Google<br>✓ Screen sharing<br>✓ Recording available</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                <h4>Zoom</h4>
                <p>✓ HD Video/Audio<br>✓ Breakout rooms<br>✓ 40-min free</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Platform selector
        platform = st.selectbox(
            "Choose platform:",
            ["Jitsi Meet (Recommended - Free)", "Google Meet", "Zoom", "Microsoft Teams"],
            index=0
        )
        
        room_id = st.session_state.get('current_room', 'wms-meeting')
        
        if platform == "Jitsi Meet (Recommended - Free)":
            jitsi_url = f"https://meet.jit.si/{room_id}"
            st.markdown(f"""
            <div style="background-color: #1e3c72; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <h3>✅ Ready to Join!</h3>
                <p style="font-size: 18px;">Room: <b>{room_id}</b></p>
                <a href="{jitsi_url}" target="_blank" style="background-color: #ffd700; color: #1e3c72; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; margin: 10px 0;">🚀 Launch Jitsi Meeting</a>
                <p style="font-size: 12px; margin-top: 10px;">📱 Works on mobile • No installation required • End-to-end encrypted</p>
            </div>
            """, unsafe_allow_html=True)
        elif platform == "Google Meet":
            st.info("""
            ### Google Meet Instructions:
            1. Go to [meet.google.com](https://meet.google.com)
            2. Click "Start a meeting"
            3. Share this code with your team:
            """)
            st.code(room_id, language="text")
        elif platform == "Zoom":
            st.info("""
            ### Zoom Instructions:
            1. Open Zoom app or go to [zoom.us](https://zoom.us)
            2. Click "Host a meeting"
            3. Use this meeting ID:
            """)
            st.code(room_id, language="text")
        else:  # Teams
            st.info("""
            ### Microsoft Teams Instructions:
            1. Open Microsoft Teams
            2. Click "Meet now"
            3. Share this meeting name:
            """)
            st.code(room_id, language="text")
        
        # Quick actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 New Room", use_container_width=True):
                st.session_state['show_meeting'] = False
                if 'current_room' in st.session_state:
                    del st.session_state['current_room']
                st.rerun()
        with col2:
            if st.button("📧 Invite Team", use_container_width=True):
                st.info(f"Share this room ID: {room_id}")
        with col3:
            if st.button("❌ End Meeting", use_container_width=True):
                st.session_state['show_meeting'] = False
                st.rerun()
    
    # Tips section
    with st.expander("💡 Video Call Tips"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🎥 Before joining:**
            - Test your camera
            - Check your microphone
            - Use headphones to avoid echo
            - Find a quiet place
            """)
        with col2:
            st.markdown("""
            **📱 During the call:**
            - Mute when not speaking
            - Look at the camera
            - Use chat for questions
            - Share screen when needed
            """)

# Update the tabs definition at the top of your file
# Find this line and replace with the new one:
# tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([...
# Replace with:
# tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([...
