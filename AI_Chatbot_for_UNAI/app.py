"""
AI Chatbot for UNAI
"""

import streamlit as st

st.set_page_config(
    page_title="UNAI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
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
        st.error("❌ Missing Supabase credentials in .env file")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ============================================================
# Authentication Functions
# ============================================================

def check_authentication():
    """Check if user is logged in"""
    if "user" not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_login_page()
        st.stop()

def show_login_page():
    """Display login/signup page"""
    st.title("🔐 UNAI Chatbot")
    st.markdown("### ล็อกอินเพื่อใช้งาน")
    
    tab1, tab2 = st.tabs(["เข้าสู่ระบบ", "สมัครสมาชิก"])
    
    with tab1:
        st.subheader("เข้าสู่ระบบ")
        email = st.text_input("อีเมล", key="login_email", placeholder="your@email.com")
        password = st.text_input("รหัสผ่าน", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("❌ กรุณากรอกอีเมลและรหัสผ่าน")
                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.session_state.user = response.user
                        st.success("✅ เข้าสู่ระบบสำเร็จ!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ เข้าสู่ระบบไม่สำเร็จ: {str(e)}")
    
    with tab2:
        st.subheader("สมัครสมาชิก")
        email = st.text_input("อีเมล", key="signup_email", placeholder="your@email.com")
        password = st.text_input("รหัสผ่าน", type="password", key="signup_password")
        confirm_password = st.text_input("ยืนยันรหัสผ่าน", type="password", key="confirm_password")
        
        if st.button("สมัครสมาชิก", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
            elif password != confirm_password:
                st.error("❌ รหัสผ่านไม่ตรงกัน")
            elif len(password) < 6:
                st.error("❌ รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")
            else:
                try:
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })
                    st.success("✅ สมัครสมาชิกสำเร็จ! กรุณาตรวจสอบอีเมลเพื่อยืนยันบัญชี")
                    st.info("💡 กลับไปที่แท็บ 'เข้าสู่ระบบ' เพื่อเข้าใช้งาน")
                except Exception as e:
                    st.error(f"❌ สมัครสมาชิกไม่สำเร็จ: {str(e)}")

def logout():
    """Logout user"""
    try:
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.chat_sessions = {}
        st.success("✅ ออกจากระบบสำเร็จ")
        st.rerun()
    except Exception as e:
        st.error(f"❌ ออกจากระบบไม่สำเร็จ: {str(e)}")

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
        st.error(f"❌ Error saving to database: {str(e)}")
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
        st.error(f"❌ Error loading from database: {str(e)}")
        return {}

def delete_session_from_db(session_id):
    """ลบแชทจาก Supabase"""
    try:
        supabase.table("chat_sessions").delete().eq("id", session_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error deleting from database: {str(e)}")
        return False

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
def inject_css():
    # Define colors
    if st.session_state.theme == "light":
        colors = {
            "bg": "#FFFFFF",
            "text": "#000000",
            "sidebar_bg": "#F8FAFC",
            "sidebar_hover": "#E2E8F0",
            "chat_user_bg": "#000000",
            "chat_user_text": "#FFFFFF",
            "chat_ai_bg": "#F1F5F9",
            "chat_ai_text": "#000000",
            "input_bg": "#FFFFFF",
            "input_text": "#000000",
            "border": "#E2E8F0",
            "btn_bg": "#FFFFFF",
            "btn_text": "#000000",
            "btn_hover": "#F1F5F9",
            "search_placeholder": "#666666",
            "popover_bg": "#FFFFFF",
            "popover_text": "#000000"
        }
    else:  # Dark theme
        colors = {
            "bg": "#000000",
            "text": "#FFFFFF",
            "sidebar_bg": "#121212",
            "sidebar_hover": "#333333",
            "chat_user_bg": "#FFFFFF",
            "chat_user_text": "#000000",
            "chat_ai_bg": "#1E1E1E",
            "chat_ai_text": "#FFFFFF",
            "input_bg": "#FFFFFF",
            "input_text": "#000000",
            "border": "#444444",
            "btn_bg": "#121212",
            "btn_text": "#FFFFFF",
            "btn_hover": "#333333",
            "search_placeholder": "#CCCCCC",
            "popover_bg": "#1E1E1E",
            "popover_text": "#FFFFFF"
        }

    st.markdown(f"""
    <style>
        /* Global Reset & Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sarabun:wght@400;500;600&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', 'Sarabun', sans-serif;
            color: {colors['text']} !important;
        }}
        
        h1, h2, h3, h4, h5, h6, .stMarkdown, p {{
            color: {colors['text']} !important;
        }}

        /* Main Background */
        .stApp {{
            background-color: {colors['bg']} !important;
        }}
        /* FIX 2: Top Bar (Always White) */
        [data-testid="stHeader"] {{
            background-color: #FFFFFF !important;
        }}
        
        [data-testid="stHeader"] * {{
            color: #000000 !important;
        }}

        /* Force all top bar elements to be visible */
        [data-testid="stHeader"] *,
        [data-testid="stToolbar"] *,
        [data-testid="stHeader"] button *,
        [data-testid="stToolbar"] button * {{
            color: #000000 !important;
        }}
        
        /* Specifically target Deploy button */
        [data-testid="stHeader"] button[kind="header"],
        [data-testid="stToolbar"] button {{
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }}
        
        /* Three dots menu */
        [data-testid="stHeader"] [data-testid="baseButton-header"],
        [data-testid="stToolbar"] [data-testid="baseButton-header"] {{
            color: #000000 !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {colors['sidebar_bg']} !important;
            border-right: 1px solid {colors['border']};
        }}
        
        [data-testid="stSidebar"] * {{
            color: {colors['text']} !important;
        }}
        
        /* Search Box */
        [data-testid="stSidebar"] input[type="text"] {{
            color: {colors['text']} !important;
            background-color: {colors['sidebar_bg']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
        }}
        
        [data-testid="stSidebar"] input[type="text"]::placeholder {{
            color: {colors['search_placeholder']} !important;
            opacity: 1;
        }}

        /* ALL BUTTONS */
        button {{
            background-color: {colors['btn_bg']} !important;
            color: {colors['btn_text']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s;
        }}

        button:hover {{
            background-color: {colors['btn_hover']} !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        /* Sidebar buttons */
        [data-testid="stSidebar"] button {{
            background-color: {colors['sidebar_bg']} !important;
            color: {colors['text']} !important;
            border: 1px solid {colors['border']} !important;
        }}

        [data-testid="stSidebar"] button:hover {{
            background-color: {colors['sidebar_hover']} !important;
        }}

        /* FIX 1: Sidebar Toggle Arrow (Force White) */
        button[kind="header"] {{
            color: #FFFFFF !important;
        }}
        
        button[kind="header"] svg {{
            fill: #FFFFFF !important;
        }}
        
        [data-testid="collapsedControl"] {{
            color: #FFFFFF !important;
        }}
        
        [data-testid="collapsedControl"] svg {{
            fill: #FFFFFF !important;
        }}
        
        /* Sidebar collapse button (another selector) */
        section[data-testid="stSidebar"] > button {{
            color: #FFFFFF !important;
        }}
        
        section[data-testid="stSidebar"] > button svg {{
            fill: #FFFFFF !important;
        }}

        /* ===== FIX POPOVER (Match Theme) ===== */
        
        /* Popover background */
        [data-baseweb="popover"] [role="dialog"] {{
            background-color: {colors['popover_bg']} !important;
            color: {colors['popover_text']} !important;
            border: 1px solid {colors['border']} !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            outline: none !important;
        }}

        [data-baseweb="popover"] > div {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        [data-testid="stPopoverBody"] {{
            background-color: {colors['popover_bg']} !important;
            color: {colors['popover_text']} !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            border: 1px solid {colors['border']} !important;
        }}
        
        /* Popover text elements */
        [data-testid="stPopoverBody"] *,
        [data-baseweb="popover"] * {{
            color: {colors['popover_text']} !important;
        }}

        [data-baseweb="layer"],
        [data-baseweb="popover"] * {{
            box-shadow: none !important;
            outline: none !important;
        }}
        
                /* Input inside popover */
        [data-baseweb="popover"] input[type="text"],
        [data-testid="stPopoverBody"] input[type="text"] {{
            background-color: {colors['popover_bg']} !important;
            color: {colors['popover_text']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
        }}

        [data-baseweb="popover"] input[type="text"]::placeholder,
        [data-testid="stPopoverBody"] input[type="text"]::placeholder {{
            color: {colors['search_placeholder']} !important;
        }}
        
        /* Divider inside popover */
        [data-testid="stPopoverBody"] hr,
        [data-baseweb="popover"] hr,
        [data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"],
        [data-baseweb="popover"] [data-testid="stHorizontalBlock"] {{
            border-color: {colors['border']} !important;
            background-color: {colors['border']} !important;
        }}
        
        /* Buttons inside popover */
        [data-testid="stPopoverBody"] button {{
            background-color: {colors['btn_bg']} !important;
            color: {colors['btn_text']} !important;
            border: 1px solid {colors['border']} !important;
        }}
        
        [data-testid="stPopoverBody"] button:hover {{
            background-color: {colors['btn_hover']} !important;
        }}

                [data-testid="stPopoverBody"] button:hover {{
            background-color: {colors['btn_hover']} !important;
        }}
        
        /* ===== FIX TOOLTIPS (Match Theme) ===== */
        
        /* Tooltip container */
        [role="tooltip"],
        [data-testid="stTooltipContent"],
        div[data-baseweb="tooltip"] {{
            background-color: {colors['popover_bg']} !important;
            color: {colors['popover_text']} !important;
            border: 1px solid {colors['border']} !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        }}
        
        /* Tooltip arrow */
        [role="tooltip"]::before,
        [role="tooltip"]::after,
        div[data-baseweb="tooltip"]::before,
        div[data-baseweb="tooltip"]::after {{
            border-top-color: {colors['popover_bg']} !important;
            border-bottom-color: {colors['popover_bg']} !important;
        }}
        
        /* Tooltip text - Force correct colors */
        [role="tooltip"] *,
        [data-testid="stTooltipContent"] *,
        div[data-baseweb="tooltip"] *,
        div[data-baseweb="tooltip"] div,
        div[data-baseweb="tooltip"] span,
        div[data-baseweb="tooltip"] p {{
            color: {colors['popover_text']} !important;
            background-color: transparent !important;
        }}
        
        /* Force parent background */
        div[data-baseweb="tooltip"] > div {{
            background-color: {colors['popover_bg']} !important;
        }}
        
        /* ===== FIX CHAT MESSAGES (Remove Duplicate/Faded Text) ===== */
        
        /* FORCE HIDE ALL DUPLICATE/FADED ELEMENTS */
        [data-testid="stChatMessage"] * {{
            opacity: 1 !important;
        }}
        
        /* Hide any faded text with rgba colors */
        [data-testid="stChatMessage"] *[style*="rgba"],
        [data-testid="stChatMessage"] *[style*="opacity: 0"],
        [data-testid="stChatMessage"] *[style*="opacity:0"],
        [data-testid="stChatMessage"] *[class*="faded"],
        [data-testid="stChatMessage"] *[class*="ghost"] {{
            display: none !important;
        }}
        
        /* Force single content display */
        [data-testid="stChatMessageContent"] > div:not(:first-child) {{
            display: none !important;
        }}
        
        /* Remove any pseudo-elements */
        [data-testid="stChatMessage"]::before,
        [data-testid="stChatMessage"]::after,
        [data-testid="stChatMessage"] *::before,
        [data-testid="stChatMessage"] *::after {{
            display: none !important;
        }}
        
        /* User message styling */
        [data-testid="stChatMessage"][data-testid*="user"] {{
            background-color: {colors['chat_user_bg']} !important;
        }}
        
        [data-testid="stChatMessage"][data-testid*="user"] * {{
            color: {colors['chat_user_text']} !important;
        }}
        
        /* AI message styling */
        [data-testid="stChatMessage"][data-testid*="assistant"] {{
            background-color: {colors['chat_ai_bg']} !important;
        }}
        
        [data-testid="stChatMessage"][data-testid*="assistant"] * {{
            color: {colors['chat_ai_text']} !important;
        }}

    </style>
    """, unsafe_allow_html=True)
    
inject_css()

# ============================================================
# Logic Functions
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

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

def toggle_language():
    st.session_state.language = "en" if st.session_state.language == "th" else "th"
    st.rerun()

# ============================================================
# Top Right Controls (Fixed)
# ============================================================
# Adjusted layout to push buttons more to the right and fix spacing
col_header_1, col_header_2, col_header_3 = st.columns([0.92, 0.04, 0.04])

with col_header_2:
    if st.button("🌙" if st.session_state.theme == "light" else "☀️", key="theme_btn", help="Toggle Theme"):
        toggle_theme()

with col_header_3:
    if st.button("TH" if st.session_state.language == "en" else "EN", key="lang_btn", help="Switch Language"):
        toggle_language()

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

# Load Assistant
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
