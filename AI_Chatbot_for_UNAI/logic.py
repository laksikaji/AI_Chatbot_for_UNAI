import os
import streamlit as st
from pinecone import Pinecone
from dotenv import load_dotenv
import hashlib
from datetime import datetime
import time
from supabase import create_client, Client

load_dotenv()

# ============================================================
# Supabase Client
# ============================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Missing Supabase credentials in .env file")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ============================================================
# Translations
# ============================================================
TRANSLATIONS = {
    "new_chat": {"th": "แชทใหม่", "en": "New Chat"},
    "search_placeholder": {"th": "ค้นหาแชท...", "en": "Search chats..."},
    "your_chats": {"th": "แชทของคุณ", "en": "Your Chats"},
    "settings": {"th": "การตั้งค่า", "en": "Settings"},
    "delete": {"th": "ลบ", "en": "Delete"},
    "rename": {"th": "เปลี่ยนชื่อ", "en": "Rename"},
    "confirm_delete": {"th": "ยืนยันการลบ?", "en": "Confirm delete?"},
    "input_placeholder": {"th": "พิมพ์ข้อความของคุณ...", "en": "Type your message..."},
    "welcome_title": {"th": "สวัสดี! มีอะไรให้ช่วยไหม?", "en": "Hello! How can I help?"},
    "welcome_subtitle": {"th": "ถามคำถามเกี่ยวกับ UNAI หรือเริ่มบทสนทนาใหม่ได้เลย", "en": "Ask anything about UNAI or start a new conversation."},
    "thinking": {"th": "กำลังคิด...", "en": "Thinking..."},
    "save": {"th": "บันทึก", "en": "Save"},
    "cancel": {"th": "ยกเลิก", "en": "Cancel"},
    "logout": {"th": "ออกจากระบบ", "en": "Logout"},
}

def t(key):
    return TRANSLATIONS.get(key, {}).get(st.session_state.language, key)

# ============================================================
# Database Functions
# ============================================================

def save_session_to_db(session_id, session_data):
    """บันทึกแชทลง Supabase"""
    try:
        user_id = st.session_state.user.id
        
        # 1. บันทึก/อัพเดต session
        session_row = {
            "id": session_id,
            "user_id": user_id,
            "title": session_data.get("title", "New Chat"),
            "thread_id": session_data.get("thread_id"),
            "created_at": session_data.get("created_at")
        }
        
        # Upsert (Insert or Update)
        supabase.table("chat_sessions").upsert(session_row).execute()
        
        # 2. ลบข้อความเก่าก่อน (เพื่อความง่าย)
        supabase.table("chat_messages").delete().eq("session_id", session_id).execute()
        
        # 3. Insert ข้อความใหม่
        if session_data.get("messages"):
            messages_to_insert = [
                {
                    "session_id": session_id,
                    "role": msg["role"],
                    "content": msg["content"]
                }
                for msg in session_data["messages"]
            ]
            supabase.table("chat_messages").insert(messages_to_insert).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        return False

def load_sessions_from_db():
    """โหลดแชททั้งหมดจาก Supabase"""
    try:
        user_id = st.session_state.user.id
        
        # 1. โหลด sessions
        response = supabase.table("chat_sessions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        
        sessions = {}
        for session in response.data:
            session_id = session["id"]
            
            # 2. โหลดข้อความของแต่ละ session
            messages_response = supabase.table("chat_messages") \
                .select("*") \
                .eq("session_id", session_id) \
                .order("created_at") \
                .execute()
            
            messages = [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                for msg in messages_response.data
            ]
            
            sessions[session_id] = {
                "title": session["title"],
                "thread_id": session["thread_id"],
                "created_at": session["created_at"],
                "messages": messages
            }
        
        return sessions
    except Exception as e:
        st.error(f"Error loading from database: {str(e)}")
        return {}

def delete_session_from_db(session_id):
    """ลบแชทจาก Supabase"""
    try:
        supabase.table("chat_sessions").delete().eq("id", session_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting from database: {str(e)}")
        return False

# ============================================================
# AI Assistant
# ============================================================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "unai-chatbot")

@st.cache_resource
def load_assistant():
    if not PINECONE_API_KEY:
        st.error("Missing PINECONE_API_KEY")
        return None
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.assistant.Assistant(ASSISTANT_NAME)

assistant = load_assistant()

# ============================================================
# Session Management Logic
# ============================================================
def create_new_chat():
    new_id = hashlib.md5(str(time.time()).encode()).hexdigest()
    
    # สร้าง thread ใหม่สำหรับแชทนี้
    try:
        thread = assistant.create_thread()
        thread_id = thread.id
    except:
        thread_id = None
    
    new_session = {
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "title": t("new_chat"),
        "thread_id": thread_id
    }
    
    st.session_state.chat_sessions[new_id] = new_session
    st.session_state.current_session_id = new_id
    
    # บันทึกลง database
    save_session_to_db(new_id, new_session)
    
    st.rerun()

def delete_chat(session_id):
    if session_id in st.session_state.chat_sessions:
        # ลบจาก database
        delete_session_from_db(session_id)
        
        # ลบจาก session state
        del st.session_state.chat_sessions[session_id]
        
        # If deleted current, switch to another or create new
        if st.session_state.current_session_id == session_id:
            if st.session_state.chat_sessions:
                st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
            else:
                create_new_chat() # Will rerun
        st.rerun()
