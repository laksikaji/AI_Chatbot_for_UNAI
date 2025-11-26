"""
AI Chatbot for UNAI - Web Interface
Streamlit App for easy access
"""

import streamlit as st
import os
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="UNAI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .main {
        background-color: #ffffff;
    }
    h1 {
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.title("🤖 UNAI AI Assistant")
    st.markdown("---")
    
    st.markdown("### 📚 เกี่ยวกับบอท")
    st.info("""
    บอทนี้สามารถตอบคำถามจากเอกสารที่ได้รับการฝึกฝนมาแล้ว
    
    **คำถามตัวอย่าง:**
    - ข้อมูลเกี่ยวกับ UNAI
    - บริการต่างๆ
    - นโยบายและระเบียบ
    """)
    
    st.markdown("---")
    st.markdown("### 💡 คำถามตัวอย่าง")
    
    example_questions = [
        "สรุปเนื้อหาในเอกสาร",
        "UNAI คืออะไร",
        "มีบริการอะไรบ้าง",
        "ติดต่อได้ที่ไหน"
    ]
    
    for q in example_questions:
        if st.button(q, key=f"example_{q}", use_container_width=True):
            st.session_state.example_question = q
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ ล้างประวัติการสนทนา", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by Pinecone AI")

# ============================================================
# Main App
# ============================================================
st.title("🤖 UNAI AI Chatbot")
st.markdown("ถามคำถามอะไรก็ได้เกี่ยวกับ UNAI!")

# Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
ASSISTANT_NAME = os.getenv('ASSISTANT_NAME', 'unai-chatbot')

# Initialize Pinecone
@st.cache_resource
def get_assistant():
    """Initialize and cache Pinecone assistant"""
    if not PINECONE_API_KEY:
        st.error("❌ ไม่พบ PINECONE_API_KEY กรุณาตั้งค่าใน .env file")
        st.stop()
    
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        return pc.assistant.Assistant(ASSISTANT_NAME)
    except Exception as e:
        st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Pinecone: {str(e)}")
        st.stop()

assistant = get_assistant()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle example question from sidebar
if "example_question" in st.session_state:
    prompt = st.session_state.example_question
    del st.session_state.example_question
else:
    prompt = st.chat_input("พิมพ์คำถามของคุณที่นี่...")

# Process user input
if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("🤔 กำลังคิด..."):
            try:
                msg = Message(content=prompt)
                response = assistant.chat(messages=[msg])
                answer = response.message.content
                st.markdown(answer)
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer
                })
            except Exception as e:
                error_msg = f"❌ เกิดข้อผิดพลาด: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    UNAI AI Chatbot | Powered by Pinecone AI | 
    <a href='mailto:support@unai.com'>ติดต่อเรา</a>
</div>
""", unsafe_allow_html=True)