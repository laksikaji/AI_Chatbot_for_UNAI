import streamlit as st
from pinecone_plugins.assistant.models.chat import Message
from logic import (
    t, 
    create_new_chat, 
    delete_chat, 
    save_session_to_db, 
    delete_session_from_db, 
    assistant
)
from login_page import logout

def show_chat_page():
    # ============================================================
    # Top Right Controls (Fixed)
    # ============================================================
    # Adjusted layout to push buttons more to the right and fix spacing
    col_header_1, col_header_2, col_header_3 = st.columns([0.92, 0.04, 0.04])

    with col_header_2:
        if st.button("🌙" if st.session_state.theme == "light" else "☀️", key="theme_btn", help="Toggle Theme"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()

    with col_header_3:
        if st.button("TH" if st.session_state.language == "en" else "EN", key="lang_btn", help="Switch Language"):
            st.session_state.language = "en" if st.session_state.language == "th" else "th"
            st.rerun()

    # ============================================================
    # Sidebar
    # ============================================================
    with st.sidebar:
        # Header
        st.title("🤖 UNAI Chat")
        
        # Show logged in user & logout button
        if "user" in st.session_state and st.session_state.user:
            st.markdown("---")
            st.caption(f"👤 {st.session_state.user.email}")
            if st.button(f"🚪 {t('logout')}", use_container_width=True):
                logout()
            st.markdown("---")
        
        # New Chat & Search
        if st.button(f" {t('new_chat')}", use_container_width=True, type="primary"):
            create_new_chat()
            
        search_query = st.text_input("", placeholder=t("search_placeholder")).lower()
        
        st.markdown(f"### {t('your_chats')}")
        
        # Sort sessions by date
        sorted_sessions = sorted(
            st.session_state.chat_sessions.items(),
            key=lambda x: x[1]['created_at'],
            reverse=True
        )
        
        # Render Chat List
        for sid, session_data in sorted_sessions:
            title = session_data.get('title', 'Untitled')
            
            # Filter by search
            if search_query and search_query not in title.lower():
                continue
                
            is_active = (sid == st.session_state.current_session_id)
            
            # We use a container for the row
            col_name, col_action = st.columns([0.8, 0.2])
            
            with col_name:
                if st.button(title, key=f"sel_{sid}", use_container_width=True, help=title):
                    st.session_state.current_session_id = sid
                    st.rerun()
                    
            with col_action:
                try:
                    with st.popover("⋮", help="Options"):
                        st.write(t("settings"))
                        
                        # Rename
                        new_name = st.text_input(t("rename"), value=title, key=f"rename_{sid}")
                        if st.button(t("save"), key=f"save_rename_{sid}"):
                            st.session_state.chat_sessions[sid]['title'] = new_name
                            save_session_to_db(sid, st.session_state.chat_sessions[sid])
                            st.rerun()
                            
                        st.divider()
                        
                        # Delete
                        if st.button(t("delete"), key=f"del_{sid}", type="primary"):
                            delete_chat(sid)
                except AttributeError:
                    # Fallback for older Streamlit versions
                    if is_active:
                        with st.expander("⚙️"):
                            new_name = st.text_input(t("rename"), value=title, key=f"rename_{sid}")
                            if st.button(t("save"), key=f"save_rename_{sid}"):
                                st.session_state.chat_sessions[sid]['title'] = new_name
                                save_session_to_db(sid, st.session_state.chat_sessions[sid])
                                st.rerun()
                            if st.button(t("delete"), key=f"del_{sid}"):
                                delete_chat(sid)

    # ============================================================
    # Main Chat Area
    # ============================================================

    # Get Current Session
    if st.session_state.current_session_id not in st.session_state.chat_sessions:
        # Fallback if session missing
        create_new_chat()

    current_session = st.session_state.chat_sessions[st.session_state.current_session_id]

    # Welcome Message if empty
    if not current_session["messages"]:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 50px;">
            <h1>{t('welcome_title')}</h1>
            <p style="color: gray;">{t('welcome_subtitle')}</p>
        </div>
        """, unsafe_allow_html=True)

    # Display Messages
    for msg in current_session["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=False)

    # Chat Input
    if prompt := st.chat_input(t("input_placeholder")):
        # Add User Message
        current_session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt, unsafe_allow_html=False)
        
        # Generate Response
        with st.chat_message("assistant"):
            # สร้าง placeholder สำหรับแสดงผล
            message_placeholder = st.empty()
            
            # แสดง spinner
            with st.spinner(t("thinking")):
                try:
                    if assistant:
                        # ใช้ thread_id แยกตามแชท
                        thread_id = current_session.get("thread_id")
                        
                        # สร้าง message
                        msg = Message(content=prompt)
                        
                        # ส่งไปยัง Pinecone พร้อม thread_id
                        if thread_id:
                            response = assistant.chat(messages=[msg], thread_id=thread_id)
                        else:
                            # ครั้งแรกของแชทนี้ - สร้าง thread ใหม่
                            response = assistant.chat(messages=[msg])
                            # เก็บ thread_id ไว้ใช้ครั้งต่อไป
                            if hasattr(response, 'thread_id'):
                                current_session["thread_id"] = response.thread_id
                        
                        reply = response.message.content
                    else:
                        reply = "Error: Assistant not initialized."
                except Exception as e:
                    reply = f"Error: {str(e)}"
            
            # แสดงคำตอบใน placeholder หลังคิดเสร็จ
            message_placeholder.write(reply)
            
        # Add AI Message
        current_session["messages"].append({"role": "assistant", "content": reply})

        # Auto-rename if it's the first message and title is default
        if len(current_session["messages"]) == 2 and current_session["title"] == t("new_chat"):
            # Simple heuristic: use first few words of prompt
            new_title = " ".join(prompt.split()[:5])
            current_session["title"] = new_title

        # บันทึกลง database
        save_session_to_db(st.session_state.current_session_id, current_session)

        st.rerun()
