"""
AI Chatbot for UNAI - Document Upload Script
สำหรับ upload เอกสารจาก Google Drive ไปยัง Pinecone Assistant
"""

import io
import time
import os
from typing import Dict, Any, List
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# Configuration
# ============================================================
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
ASSISTANT_NAME = os.getenv('ASSISTANT_NAME', 'unai-chatbot')
FOLDER_ID = os.getenv('FOLDER_ID')

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# ============================================================
# Functions
# ============================================================

def print_header(title: str):
    """พิมพ์ header สวยๆ"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def authenticate_google_drive():
    """
    Authenticate กับ Google Drive API
    ครั้งแรกจะเปิด browser ให้ login
    ครั้งต่อไปจะใช้ token ที่บันทึกไว้
    """
    print("🔐 Authenticating Google Drive...")
    creds = None
    
    # ตรวจสอบว่ามี token บันทึกไว้หรือยัง
    if os.path.exists('token.pickle'):
        print("   → Found saved token")
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # ถ้าไม่มี credentials หรือหมดอายุ
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("   → Refreshing expired token")
            creds.refresh(Request())
        else:
            # ต้องมีไฟล์ credentials.json
            if not os.path.exists('credentials.json'):
                print("\n❌ Error: credentials.json not found!")
                print("\n📝 How to get credentials.json:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create/Select a project")
                print("3. Enable Google Drive API")
                print("4. Create OAuth 2.0 credentials (Desktop app)")
                print("5. Download as 'credentials.json'")
                print("6. Place it in this folder\n")
                return None
            
            print("   → Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # บันทึก token สำหรับครั้งถัดไป
        print("   → Saving token for future use")
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    print("✅ Google Drive authenticated successfully\n")
    return build('drive', 'v3', credentials=creds)

def initialize_pinecone(api_key: str, assistant_name: str):
    """Initialize Pinecone และสร้าง/เชื่อมต่อ Assistant"""
    print("🔧 Initializing Pinecone...")
    
    try:
        pc = Pinecone(api_key=api_key)
        print("✅ Pinecone connected\n")
    except Exception as e:
        print(f"❌ Failed to connect to Pinecone: {str(e)}\n")
        return None
    
    print(f"🤖 Setting up Assistant: '{assistant_name}'...")
    
    try:
        # ลองเชื่อมต่อกับ Assistant ที่มีอยู่
        assistant = pc.assistant.Assistant(assistant_name)
        print(f"✅ Found existing assistant: {assistant_name}\n")
    except Exception:
        # ถ้าไม่มีให้สร้างใหม่
        print(f"   → Creating new assistant...")
        try:
            assistant = pc.assistant.create_assistant(
                assistant_name=assistant_name,
                instructions=(
                    "คุณคือ AI Assistant สำหรับองค์กร UNAI "
                    "ตอบคำถามอย่างชัดเจน กระชับ และเป็นมิตร "
                    "โดยอ้างอิงจากเอกสารที่ได้รับเท่านั้น "
                    "ถ้าไม่มีข้อมูลในเอกสารให้บอกตรงๆ ว่าไม่มีข้อมูล"
                ),
                timeout=60
            )
            print(f"✅ Assistant created successfully\n")
        except Exception as e:
            print(f"❌ Failed to create assistant: {str(e)}\n")
            return None
    
    return assistant

def list_documents_in_folder(drive_service, folder_id: str) -> List[Dict]:
    """ดึงรายชื่อเอกสารทั้งหมดจาก Google Drive folder"""
    print(f"📂 Scanning Google Drive folder...")
    print(f"   Folder ID: {folder_id}\n")
    
    try:
        # ค้นหาทั้ง PDF และ Google Docs
        query = (
            f"'{folder_id}' in parents and "
            f"(mimeType='application/pdf' or "
            f"mimeType='application/vnd.google-apps.document')"
        )
        
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)'
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("⚠️  No documents found in folder\n")
            return []
        
        print(f"📄 Found {len(files)} document(s):")
        for idx, file in enumerate(files, 1):
            file_type = "PDF" if "pdf" in file['mimeType'] else "Google Doc"
            print(f"   {idx}. {file['name']} ({file_type})")
        print()
        
        # ดาวน์โหลดแต่ละไฟล์
        documents = []
        for idx, item in enumerate(files, 1):
            print(f"[{idx}/{len(files)}] Processing: {item['name']}")
            
            # ถ้าเป็น Google Doc ให้ export เป็น PDF
            if item['mimeType'] == 'application/vnd.google-apps.document':
                print(f"   → Converting Google Doc to PDF...")
                request = drive_service.files().export_media(
                    fileId=item['id'],
                    mimeType='application/pdf'
                )
            else:
                print(f"   → Downloading PDF...")
                request = drive_service.files().get_media(fileId=item['id'])
            
            # ดาวน์โหลดไฟล์
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"   → Progress: {progress}%", end='\r')
            
            fh.seek(0)
            documents.append({
                'id': item['id'],
                'name': item['name'].replace('.pdf', ''),
                'pdf_content': fh.getvalue()
            })
            print(f"   ✅ Downloaded successfully\n")
        
        return documents
        
    except HttpError as error:
        print(f'❌ Google Drive API error: {error}\n')
        return []

def upload_to_pinecone(
    api_key: str,
    assistant_name: str,
    pdf_document: Dict[str, Any]
) -> bool:
    """Upload PDF ไปยัง Pinecone Assistant"""
    url = f"https://prod-1-data.ke.pinecone.io/assistant/files/{assistant_name}"
    headers = {"Api-Key": api_key}
    file_obj = io.BytesIO(pdf_document['pdf_content'])
    filename = f"{pdf_document['name']}.pdf"
    
    try:
        response = requests.post(
            url,
            headers=headers,
            files={'file': (filename, file_obj, 'application/pdf')},
            timeout=60
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"   ❌ Upload failed: {str(e)}")
        return False
    finally:
        file_obj.close()

def wait_for_processing(assistant, max_wait_time=180):
    """รอให้ Pinecone ประมวลผลไฟล์เสร็จ"""
    print("⏳ Waiting for Pinecone to process files...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # ทดสอบว่าไฟล์พร้อมหรือยัง
            test_msg = Message(content="test")
            assistant.chat(messages=[test_msg])
            elapsed = int(time.time() - start_time)
            print(f"✅ Files processed successfully! (took {elapsed}s)\n")
            return True
        except Exception as e:
            error_msg = str(e)
            if "still be processing" in error_msg or "No files found" in error_msg:
                elapsed = int(time.time() - start_time)
                print(f"   Still processing... ({elapsed}s elapsed)", end='\r')
                time.sleep(10)
            else:
                print(f"\n❌ Unexpected error: {error_msg}\n")
                return False
    
    print(f"\n⚠️  Timeout after {max_wait_time}s\n")
    return False

# ============================================================
# Main Function
# ============================================================

def main():
    """Main execution function"""
    
    print_header("🚀 AI Chatbot for UNAI - Document Upload")
    
    # ตรวจสอบ configuration
    print("🔍 Checking configuration...")
    
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in .env file\n")
        return
    print("   ✅ Pinecone API key found")
    
    if not FOLDER_ID:
        print("❌ Error: FOLDER_ID not found in .env file\n")
        return
    print("   ✅ Google Drive folder ID found")
    
    print(f"   ✅ Assistant name: {ASSISTANT_NAME}\n")
    
    # Authenticate Google Drive
    drive_service = authenticate_google_drive()
    if not drive_service:
        return
    
    # Initialize Pinecone
    assistant = initialize_pinecone(PINECONE_API_KEY, ASSISTANT_NAME)
    if not assistant:
        return
    
    # Get documents from Google Drive
    documents = list_documents_in_folder(drive_service, FOLDER_ID)
    if not documents:
        return
    
    # Upload documents to Pinecone
    print_header("📤 Uploading Documents to Pinecone")
    
    success_count = 0
    for idx, doc in enumerate(documents, 1):
        print(f"[{idx}/{len(documents)}] Uploading: {doc['name']}")
        
        if upload_to_pinecone(PINECONE_API_KEY, ASSISTANT_NAME, doc):
            print(f"   ✅ Upload successful\n")
            success_count += 1
        else:
            print()
        
        time.sleep(1)  # หน่วงเวลาเล็กน้อยระหว่างการ upload
    
    print_header(f"✅ Upload Summary")
    print(f"Total documents: {len(documents)}")
    print(f"Successfully uploaded: {success_count}")
    print(f"Failed: {len(documents) - success_count}\n")
    
    # Wait for processing
    if success_count > 0:
        wait_for_processing(assistant)
        print_header("🎉 Setup Complete!")
        print("Your chatbot is ready to use!")
        print("Run 'python chat.py' to start asking questions.\n")
    else:
        print("⚠️  No documents were uploaded successfully.\n")

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}\n")