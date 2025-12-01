import streamlit as st

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
