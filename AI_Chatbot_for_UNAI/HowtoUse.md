# 📚 คู่มือการสร้าง AI Chatbot ด้วย Pinecone และ Streamlit

> คู่มือสำหรับสร้าง AI Chatbot ที่ตอบคำถามจากเอกสาร พร้อม Deploy ขึ้นเว็บ
> 
> ⚠️ **หมายเหตุ:** ตัวอย่างในคู่มือนี้ใช้ชื่อสมมติ เปลี่ยนเป็นชื่อโปรเจคของคุณได้

---

## 📑 สารบัญ

1. [ภาพรวมโปรเจค](#ภาพรวมโปรเจค)
2. [สิ่งที่ต้องเตรียม](#สิ่งที่ต้องเตรียม)
3. [ขั้นตอนที่ 1: ตั้งค่า Pinecone](#ขั้นตอนที่-1-ตั้งค่า-pinecone)
4. [ขั้นตอนที่ 2: ตั้งค่า Google Cloud (Optional)](#ขั้นตอนที่-2-ตั้งค่า-google-cloud-optional)
5. [ขั้นตอนที่ 3: สร้างโปรเจค](#ขั้นตอนที่-3-สร้างโปรเจค)
6. [ขั้นตอนที่ 4: เขียนโค้ด](#ขั้นตอนที่-4-เขียนโค้ด)
7. [ขั้นตอนที่ 5: ทดสอบ Local](#ขั้นตอนที่-5-ทดสอบ-local)
8. [ขั้นตอนที่ 6: Deploy ขึ้นเว็บ](#ขั้นตอนที่-6-deploy-ขึ้นเว็บ)
9. [แก้ปัญหาที่พบบ่อย](#แก้ปัญหาที่พบบ่อย)

---

## ภาพรวมโปรเจค

### 🎯 เป้าหมาย
สร้าง AI Chatbot ที่:
- ✅ ตอบคำถามจากเอกสารที่อัปโหลด
- ✅ มีหน้าเว็บสวยงาม
- ✅ Deploy ขึ้นเว็บใช้ได้ 24/7
- ✅ แชร์ URL ให้คนอื่นใช้

### 🏗️ สถาปัตยกรรม
```
[เอกสาร] → [Pinecone AI] → [Streamlit Web] → [ผู้ใช้งาน]
```

### ⏱️ เวลาที่ใช้
- ตั้งค่า Pinecone: 15 นาที
- เขียนโค้ด: 30-60 นาที
- Deploy: 10 นาที
- **รวม: 1-2 ชั่วโมง**

---

## สิ่งที่ต้องเตรียม

### 📦 Software
- **Python 3.10+** - [ดาวน์โหลด](https://www.python.org/downloads/)
- **Git** - [ดาวน์โหลด](https://git-scm.com/downloads)
- **Text Editor** - VS Code, Notepad++ หรือ Notepad ธรรมดา
- **PowerShell/Terminal** - สำหรับรันคำสั่ง

### 🌐 Accounts (ฟรีทั้งหมด)
- **Pinecone** - [สมัคร](https://www.pinecone.io/)
- **GitLab/GitHub** - [สมัคร](https://gitlab.com/)
- **Streamlit Cloud** - [สมัคร](https://streamlit.io/cloud) (สำหรับ Deploy)
- **Google Cloud** - [สมัคร](https://console.cloud.google.com/) (Optional)

### ✅ ตรวจสอบความพร้อม
```powershell
# ตรวจสอบ Python
python --version
# ควรได้: Python 3.10.x หรือสูงกว่า

# ตรวจสอบ pip
pip --version

# ตรวจสอบ Git
git --version
```

---

## ขั้นตอนที่ 1: ตั้งค่า Pinecone

### 1.1 สมัครและเข้าสู่ระบบ

1. ไปที่ https://www.pinecone.io/
2. คลิก **"Sign Up"** (สมัครด้วย Email/Google/GitHub)
3. ยืนยันอีเมล
4. เข้าสู่ **Pinecone Dashboard**

---

### 1.2 สร้าง API Key

1. ใน Dashboard → ไปที่ **"API Keys"**
2. คลิก **"Create API Key"**
3. ตั้งชื่อ: `My-Chatbot-Key`
4. คัดลอก API Key (ขึ้นต้นด้วย `pcsk_...`)
5. **⚠️ เก็บ API Key ไว้ปลอดภัย!**

**ตัวอย่าง API Key:**
```
pcsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 1.3 สร้าง Assistant

1. Dashboard → **"Assistants"** → **"Create Assistant"**
2. ตั้งค่า:
   - **Name:** `my-chatbot` (หรือชื่อที่ต้องการ)
   - **Model:** `gpt-4` หรือ `gpt-3.5-turbo`
   - **Instructions:** `คุณเป็น AI ผู้ช่วยตอบคำถามจากเอกสาร ตอบเป็นภาษาไทย กระชับ เป็นมิตร`
3. คลิก **"Create"**
4. จดชื่อ Assistant: `my-chatbot`

---

### 1.4 อัปโหลดเอกสาร

1. เข้า Assistant ที่สร้าง
2. คลิก **"Upload Files"** หรือ **"Knowledge Base"**
3. เลือกไฟล์:
   - รองรับ: PDF, TXT, DOCX, MD
   - ขนาดไฟล์: สูงสุด 512 MB รวม (Free tier)
4. รอประมวลผล (1-5 นาที)
5. เสร็จ! เอกสารพร้อมใช้งาน

**💡 Tips:**
- อัปโหลดทีละหลายไฟล์ได้
- ไฟล์ควรมีเนื้อหาชัดเจน ไม่ใช่แค่รูปภาพ
- PDF ที่สแกนมาต้องผ่าน OCR ก่อน

---

## ขั้นตอนที่ 2: ตั้งค่า Google Cloud (Optional)

> ⚠️ **ข้ามขั้นตอนนี้ได้** ถ้าไม่ต้องการเชื่อม Google Drive/Gmail

### 2.1 สร้าง Google Cloud Project

1. ไปที่: https://console.cloud.google.com/
2. คลิก **"New Project"**
3. ตั้งชื่อ: `My-Chatbot-Project`
4. คลิก **"Create"**

---

### 2.2 เปิด APIs

1. **APIs & Services** → **"Library"**
2. ค้นหาและเปิดใช้งาน:
   - ✅ Google Drive API
   - ✅ Gmail API
3. คลิก **"Enable"** แต่ละตัว

---

### 2.3 สร้าง OAuth Credentials

1. **APIs & Services** → **"Credentials"**
2. คลิก **"Create Credentials"** → **"OAuth Client ID"**
3. เลือก: **Desktop App**
4. ตั้งชื่อ: `My-Desktop-Client`
5. คลิก **"Create"**
6. **ดาวน์โหลด JSON**
7. เปลี่ยนชื่อไฟล์เป็น: `credentials.json`

---

### 2.4 ตั้งค่า OAuth Consent Screen

1. **APIs & Services** → **"OAuth consent screen"**
2. เลือก: **External**
3. กรอก:
   - **App name:** My AI Chatbot
   - **User support email:** your-email@gmail.com
   - **Developer contact:** your-email@gmail.com
4. **Scopes:** เพิ่ม
   - `.../auth/drive.readonly`
   - `.../auth/gmail.readonly`
5. **Test users:** เพิ่ม `your-email@gmail.com`
6. คลิก **"Save and Continue"**

---

## ขั้นตอนที่ 3: สร้างโปรเจค

### 3.1 สร้างโครงสร้าง

```powershell
# สร้าง folder
cd C:\
mkdir "Projects"
cd "Projects"

# สร้าง Git repo
mkdir my_ai_chatbot
cd my_ai_chatbot
git init

# สร้าง folder โปรเจค
mkdir chatbot
cd chatbot
```

**โครงสร้างที่ได้:**
```
C:\Projects\my_ai_chatbot/
├── .git/
└── chatbot/
```

---

### 3.2 สร้างไฟล์ .env

```powershell
notepad .env
```

**เนื้อหา:**
```env
# Pinecone Configuration
PINECONE_API_KEY=pcsk_your_api_key_here
ASSISTANT_NAME=my-chatbot

# Google Cloud (Optional)
GOOGLE_CREDENTIALS_PATH=credentials.json
```

**⚠️ แทนที่:**
- `pcsk_your_api_key_here` → API Key จริงจาก Pinecone
- `my-chatbot` → ชื่อ Assistant ที่สร้าง

---

### 3.3 สร้างไฟล์ requirements.txt

```powershell
notepad requirements.txt
```

**เนื้อหา:**
```txt
python-dotenv==1.0.0
pinecone-client==3.0.0
pinecone-plugin-assistant==0.0.9
streamlit==1.31.0
google-api-python-client==2.187.0
google-auth-httplib2==0.2.1
google-auth-oauthlib==1.2.3
requests==2.32.4
```

---

### 3.4 สร้างไฟล์ .gitignore

```powershell
# ถ้าอยู่ใน chatbot ให้ย้ายไป root
cd ..
notepad .gitignore
```

**เนื้อหา:**
```txt
# ไฟล์ที่ห้าม commit ขึ้น Git
.env
credentials.json
token.pickle

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log
```

---

### 3.5 ติดตั้ง Dependencies

```powershell
cd chatbot
python -m pip install -r requirements.txt
```

**รอติดตั้ง (2-5 นาที)**

**ถ้าเจอ error:**
- `cmake failed` → ลองติดตั้ง: `pip install pyarrow==14.0.1`
- `No module named 'blinker'` → ติดตั้ง: `pip install blinker`
- `No module named 'toml'` → ติดตั้ง: `pip install toml`

---

## ขั้นตอนที่ 4: เขียนโค้ด

### 4.1 สร้างไฟล์ app.py

```powershell
notepad app.py
```

**วางโค้ดนี้:**

```python
"""
AI Chatbot - Web Interface
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
    page_title="AI Chatbot",
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
    st.title("🤖 AI Assistant")
    st.markdown("---")
    
    st.markdown("### 📚 เกี่ยวกับบอท")
    st.info("""
    บอทนี้สามารถตอบคำถามจากเอกสารที่ได้รับการฝึกฝนมาแล้ว
    
    **คำถามตัวอย่าง:**
    - สรุปเนื้อหาในเอกสาร
    - ข้อมูลที่ต้องการค้นหา
    - คำถามอื่นๆ
    """)
    
    st.markdown("---")
    st.markdown("### 💡 คำถามตัวอย่าง")
    
    example_questions = [
        "สรุปเนื้อหาในเอกสาร",
        "ข้อมูลสำคัญคืออะไร",
        "มีหัวข้อหลักอะไรบ้าง",
        "สามารถติดต่อได้ที่ไหน"
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
st.title("🤖 AI Chatbot")
st.markdown("ถามคำถามอะไรก็ได้เกี่ยวกับเอกสาร!")

# Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
ASSISTANT_NAME = os.getenv('ASSISTANT_NAME', 'my-chatbot')

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
    AI Chatbot | Powered by Pinecone AI
</div>
""", unsafe_allow_html=True)
```

**บันทึกไฟล์ (Ctrl + S)**

---

### 4.2 สร้างไฟล์ README.md (Optional)

```powershell
cd ..
notepad README.md
```

**เนื้อหา:**
```markdown
# 🤖 AI Chatbot

AI Chatbot ที่ตอบคำถามจากเอกสาร ด้วย Pinecone และ Streamlit

## ✨ Features
- ตอบคำถามจากเอกสารที่อัปโหลด
- หน้าเว็บสวยงามด้วย Streamlit
- Deploy ได้บน Streamlit Cloud

## 🚀 วิธีใช้งาน

### ติดตั้ง
```bash
pip install -r chatbot/requirements.txt
```

### รัน Local
```bash
cd chatbot
streamlit run app.py
```

## 📝 Configuration
แก้ไขไฟล์ `.env`:
- `PINECONE_API_KEY`: API Key จาก Pinecone
- `ASSISTANT_NAME`: ชื่อ Assistant ที่สร้าง

## 📄 License
MIT License
```

---

## ขั้นตอนที่ 5: ทดสอบ Local

### 5.1 รันเว็บ

```powershell
cd "C:\Projects\my_ai_chatbot\chatbot"
python -m streamlit run app.py
```

**ผลลัพธ์:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

**เบราว์เซอร์จะเปิดอัตโนมัติที่: `http://localhost:8501`**

---

### 5.2 ทดสอบการทำงาน

**ตรวจสอบ:**
- ✅ เว็บเปิดได้
- ✅ แสดง UI ครบถ้วน
- ✅ พิมพ์คำถามได้
- ✅ บอทตอบคำถามได้
- ✅ ประวัติการสนทนาแสดง
- ✅ ปุ่มตัวอย่างคำถามทำงาน
- ✅ ปุ่มล้างประวัติทำงาน

**ถ้าเจอ error:**
- ตรวจสอบ `.env` → API Key ถูกต้องไหม
- ตรวจสอบ Assistant Name → ชื่อตรงกับที่สร้างใน Pinecone ไหม
- ตรวจสอบ Internet → เชื่อมต่อได้ไหม

---

### 5.3 ทดสอบคำถาม

**ลองถามคำถามเหล่านี้:**
1. "สรุปเนื้อหาในเอกสาร"
2. "ข้อมูลสำคัญคืออะไร"
3. "มีหัวข้อหลักอะไรบ้าง"
4. "สามารถติดต่อได้ที่ไหน"

**ถ้าตอบได้ถูกต้อง → สำเร็จ! ✅**

---

## ขั้นตอนที่ 6: Deploy ขึ้นเว็บ

### 6.1 Push โค้ดขึ้น GitLab

#### สร้าง Repository บน GitLab:
1. ไปที่: https://gitlab.com
2. คลิก **"New Project"** → **"Create blank project"**
3. ตั้งค่า:
   - **Project name:** `my_ai_chatbot` (หรือชื่อที่ต้องการ)
   - **Visibility:** Private
4. คลิก **"Create Project"**
5. **คัดลอก URL** (เช่น `https://gitlab.com/your-username/my_ai_chatbot.git`)

#### Push โค้ด:
```powershell
cd "C:\Projects\my_ai_chatbot"

# Add remote
git remote add origin https://gitlab.com/your-username/my_ai_chatbot.git

# Commit
git add .
git commit -m "Initial commit: AI Chatbot"

# Push
git branch -M main
git push -u origin main
```

---

### 6.2 Deploy บน Streamlit Cloud

#### ขั้นตอน:
1. **ไปที่:** https://streamlit.io/cloud
2. **Sign up/Login** (ใช้ GitHub/GitLab/Email)
3. คลิก **"New app"**
4. เชื่อม GitLab account
5. เลือก:
   - **Repository:** `my_ai_chatbot`
   - **Branch:** `main`
   - **Main file path:** `chatbot/app.py`
6. **Advanced settings** → **Secrets:**
   ```
   PINECONE_API_KEY = "pcsk_your_api_key_here"
   ASSISTANT_NAME = "my-chatbot"
   ```
7. คลิก **"Deploy!"**
8. รอ 2-3 นาที
9. **เสร็จ!** ได้ URL: `https://your-app-name.streamlit.app`

---

### 6.3 แชร์ URL

**คัดลอก URL แล้วแชร์:**
- ทีมงาน
- ลูกค้า
- ผู้ใช้งาน

**URL จะใช้งานได้ตลอด 24/7!** 🎉

---

## แก้ปัญหาที่พบบ่อย

### ❌ `ModuleNotFoundError: No module named 'streamlit'`

**แก้ไข:**
```powershell
pip install streamlit
```

---

### ❌ `ModuleNotFoundError: No module named 'blinker'`

**แก้ไข:**
```powershell
pip install blinker toml
```

---

### ❌ `error: command 'cmake' failed`

**แก้ไข:**
```powershell
pip install pyarrow==14.0.1
pip install streamlit
```

---

### ❌ `ไม่พบ PINECONE_API_KEY`

**ตรวจสอบ:**
1. ไฟล์ `.env` อยู่ใน folder `chatbot/` ใช่ไหม
2. เปิดไฟล์ `.env` → API Key ถูกต้องไหม
3. ไม่มีเว้นวรรคหรืออักขระพิเศษ
4. รัน Streamlit อยู่ใน folder เดียวกับ `.env`

---

### ❌ `Assistant not found`

**แก้ไข:**
1. เข้า Pinecone Dashboard
2. ตรวจสอบชื่อ Assistant
3. แก้ไขใน `.env` → `ASSISTANT_NAME=ชื่อที่ถูกต้อง`

---

### ❌ Deploy แล้วเว็บ error

**ตรวจสอบ:**
1. Streamlit Cloud → **Logs**
2. ตรวจสอบ Secrets → API Key ใส่ถูกไหม
3. ตรวจสอบ Main file path → ถูก path ไหม

---

## 🎉 สรุป

**คุณได้สร้างสำเร็จ:**
- ✅ AI Chatbot ที่ตอบคำถามจากเอกสาร
- ✅ หน้าเว็บสวยงามด้วย Streamlit
- ✅ Deploy ขึ้นเว็บใช้ได้ 24/7
- ✅ แชร์ URL ให้คนอื่นใช้

**ขั้นตอนต่อไป:**
- 🎨 ปรับแต่งหน้าเว็บ (สี, โลโก้)
- 🤖 เพิ่มฟีเจอร์ (อัปโหลดไฟล์, ส่งออก PDF)
- 📚 อัปเดทเอกสารใหม่
- 🔐 เพิ่มระบบ Login (ถ้าต้องการ)

---

## 📞 ติดต่อ & สนับสนุน

- 📧 Email: support@example.com
- 🌐 Website: https://example.com
- 💬 Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

**สร้างโดย:** UNAI Team  
**เวอร์ชัน:** 1.0.0  
**อัปเดทล่าสุด:** พฤศจิกายน 2024