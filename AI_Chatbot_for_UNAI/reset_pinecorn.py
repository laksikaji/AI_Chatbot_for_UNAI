"""
Reset Pinecone Assistant - ลบและสร้างใหม่
"""

import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
ASSISTANT_NAME = os.getenv('ASSISTANT_NAME', 'unai-chatbot')

def reset_assistant():
    """ลบ Assistant เดิมและสร้างใหม่"""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    try:
        # 1. ลบ Assistant เดิม
        print(f"🗑️  Deleting existing assistant: {ASSISTANT_NAME}...")
        pc.assistant.delete_assistant(assistant_name=ASSISTANT_NAME)
        print("✅ Assistant deleted successfully!")
    except Exception as e:
        print(f"⚠️  No existing assistant to delete: {str(e)}")
    
    try:
        # 2. สร้าง Assistant ใหม่
        print(f"\n🔧 Creating new assistant: {ASSISTANT_NAME}...")
        assistant = pc.assistant.create_assistant(
            assistant_name=ASSISTANT_NAME,
            instructions="You are a helpful AI assistant for UNAI."
        )
        print("✅ New assistant created successfully!")
        print(f"📝 Assistant Name: {assistant.name}")
        
    except Exception as e:
        print(f"❌ Error creating assistant: {str(e)}")

if __name__ == "__main__":
    print("============================================================")
    print("  🔄 Pinecone Assistant Reset")
    print("============================================================\n")
    
    confirm = input("⚠️  This will DELETE all data in Pinecone. Continue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        reset_assistant()
        print("\n🎉 Reset complete! Now run 'python upload_documents.py' to upload new documents.")
    else:
        print("❌ Reset cancelled.")