"""
AI Chatbot for UNAI
"""

import streamlit as st
import time
import hashlib
from datetime import datetime

st.set_page_config(
    page_title="UNAI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
from styles import inject_css
from login_page import check_authentication
from logic import (
    load_sessions_from_db, 
    save_session_to_db, 
    t
)
from chat_page import show_chat_page

# ============================================================
# Check Authentication
# ============================================================
check_authentication()

# ============================================================
# State Management
# ============================================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "language" not in st.session_state:
    st.session_state.language = "th"

# ============================================================
# Load Sessions from Database (After Authentication)
# ============================================================
if "chat_sessions" not in st.session_state:
    # โหลดจาก database
    loaded_sessions = load_sessions_from_db()
    
    if loaded_sessions:
        st.session_state.chat_sessions = loaded_sessions
        # ตั้ง current_session_id เป็น session แรก
        st.session_state.current_session_id = list(loaded_sessions.keys())[0]
    else:
        # ถ้าไม่มีข้อมูล สร้างแชทแรก
        new_id = hashlib.md5(str(time.time()).encode()).hexdigest()
        new_session = {
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "title": t("new_chat"),
            "thread_id": None
        }
        st.session_state.chat_sessions = {new_id: new_session}
        st.session_state.current_session_id = new_id
        
        # บันทึกลง database
        save_session_to_db(new_id, new_session)

if "current_session_id" not in st.session_state:
    # Fallback ถ้ายังไม่มี
    if st.session_state.chat_sessions:
        st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]

if "renaming_session_id" not in st.session_state:
    st.session_state.renaming_session_id = None

# ============================================================
# CSS & Theme
# ============================================================
inject_css()

# ============================================================
# Main App Logic
# ============================================================
show_chat_page()
