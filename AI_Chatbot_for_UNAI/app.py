"""
AI Chatbot for UNAI - Premium Redesign
"""

import streamlit as st
import os
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
from dotenv import load_dotenv
import hashlib
from datetime import datetime
import time

load_dotenv()

# ============================================================
# Page Config
# ============================================================
st.set_page_config(
    page_title="UNAI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# State Management
# ============================================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "language" not in st.session_state:
    st.session_state.language = "th"

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_session_id" not in st.session_state:
    # Create initial session
    new_id = hashlib.md5(str(time.time()).encode()).hexdigest()
    st.session_state.chat_sessions[new_id] = {
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "title": "New Chat"
    }
    st.session_state.current_session_id = new_id

if "renaming_session_id" not in st.session_state:
    st.session_state.renaming_session_id = None

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
}

def t(key):
    return TRANSLATIONS.get(key, {}).get(st.session_state.language, key)

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
            background-color: {colors['input_bg']} !important;
            color: {colors['input_text']} !important;
            border: 1px solid {colors['border']} !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
        }}

        [data-baseweb="popover"] input[type="text"]::placeholder,
        [data-testid="stPopoverBody"] input[type="text"]::placeholder {{
            color: {colors['search_placeholder']} !important;
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
        /* ===== FIX TOOLTIPS (Match Theme) ===== */
        
        /* Tooltip container */
        [role="tooltip"],
        [data-testid="stTooltipContent"],
        div[data-baseweb="tooltip"] {{
            background-color: {colors['popover_bg']} !important;
            color: {colors['popover_text']} !important;
            border: 1px solid {colors['border']} !important;
        }}
        
        /* Tooltip arrow */
        [role="tooltip"]::before,
        [role="tooltip"]::after,
        div[data-baseweb="tooltip"]::before,
        div[data-baseweb="tooltip"]::after {{
            border-top-color: {colors['popover_bg']} !important;
            border-bottom-color: {colors['popover_bg']} !important;
        }}
        
        /* Tooltip text */
        [role="tooltip"] *,
        [data-testid="stTooltipContent"] *,
        div[data-baseweb="tooltip"] * {{
            color: {colors['popover_text']} !important;
        }}

    </style>
    """, unsafe_allow_html=True)
    
inject_css()

# ============================================================
# Logic Functions
# ============================================================
def create_new_chat():
    new_id = hashlib.md5(str(time.time()).encode()).hexdigest()
    st.session_state.chat_sessions[new_id] = {
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "title": t("new_chat")
    }
    st.session_state.current_session_id = new_id
    st.rerun()

def delete_chat(session_id):
    if session_id in st.session_state.chat_sessions:
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
# We create a 3-column layout: Spacer (85%), Theme (7%), Lang (8%)
col_header_1, col_header_2, col_header_3 = st.columns([0.85, 0.07, 0.08])

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
    
    # New Chat & Search
    if st.button(f"➕ {t('new_chat')}", use_container_width=True, type="primary"):
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
            
        # Layout for each chat item
        # We use an expander or columns. 
        # To achieve "Click to select" AND "Rename/Delete", we can use an expander for the active one,
        # or just simple buttons.
        
        is_active = (sid == st.session_state.current_session_id)
        
        # Visual indicator for active chat
        prefix = "🔵 " if is_active else "💬 "
        
        # We use a container for the row
        col_name, col_action = st.columns([0.8, 0.2])
        
        with col_name:
            if st.button(f"{prefix}{title}", key=f"sel_{sid}", use_container_width=True, help=title):
                st.session_state.current_session_id = sid
                st.rerun()
                
        with col_action:
            # Only show actions if active or if we want to clutter the UI. 
            # Let's show a "..." popover or expander if possible. 
            # Streamlit 1.30+ has st.popover. Assuming we have a recent version.
            # If not, we fallback to an expander.
            try:
                with st.popover("⋮", help="Options"):
                    st.write(t("settings"))
                    
                    # Rename
                    new_name = st.text_input(t("rename"), value=title, key=f"rename_{sid}")
                    if st.button(t("save"), key=f"save_rename_{sid}"):
                        st.session_state.chat_sessions[sid]['title'] = new_name
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
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input(t("input_placeholder")):
    # Add User Message
    current_session["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner(t("thinking")):
            try:
                if assistant:
                    response = assistant.chat(messages=[Message(content=prompt)])
                    reply = response.message.content
                else:
                    reply = "Error: Assistant not initialized."
            except Exception as e:
                reply = f"Error: {str(e)}"
        st.markdown(reply)
        
    # Add AI Message
    current_session["messages"].append({"role": "assistant", "content": reply})
    
    # Auto-rename if it's the first message and title is default
    if len(current_session["messages"]) == 2 and current_session["title"] == t("new_chat"):
        # Simple heuristic: use first few words of prompt
        new_title = " ".join(prompt.split()[:5])
        current_session["title"] = new_title
        st.rerun()
