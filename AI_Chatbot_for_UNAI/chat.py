"""
AI Chatbot for UNAI - Chat Interface
สำหรับถามคำถามกับ chatbot
"""

import os
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
ASSISTANT_NAME = os.getenv('ASSISTANT_NAME', 'unai-chatbot')

# ============================================================
# Functions
# ============================================================

def print_header():
    """พิมพ์ header"""
    print("\n" + "="*60)
    print("  🤖 AI Chatbot for UNAI")
    print("="*60)
    print("Type your questions below. Type 'quit' to exit.")
    print("="*60 + "\n")

def ask(question: str) -> str:
    """ถามคำถามกับ chatbot"""
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        assistant = pc.assistant.Assistant(ASSISTANT_NAME)
        
        msg = Message(content=question)
        resp = assistant.chat(messages=[msg])
        
        return resp.message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

def interactive_mode():
    """โหมดแชทแบบ interactive"""
    print_header()
    
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in .env file")
        print("Please set your API key in .env file\n")
        return
    
    print("✅ Connected to chatbot\n")
    
    while True:
        try:
            # รับคำถามจากผู้ใช้
            question = input("You: ").strip()
            
            # ตรวจสอบคำสั่งพิเศษ
            if question.lower() in ['quit', 'exit', 'q', 'ออก', 'พอ']:
                print("\n👋 Goodbye! See you next time.\n")
                break
            
            if not question:
                continue
            
            # ถามคำถาม
            print("Bot: ", end="", flush=True)
            answer = ask(question)
            print(answer + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! See you next time.\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")

def single_question_mode(question: str):
    """โหมดถามคำถามเดียว"""
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in .env file\n")
        return
    
    print(f"\n❓ Question: {question}")
    print("-" * 60)
    answer = ask(question)
    print(f"💬 Answer:\n{answer}")
    print("-" * 60 + "\n")

# ============================================================
# Main Function
# ============================================================

def main():
    """Main execution function"""
    import sys
    
    # ตรวจสอบว่ามี argument ส่งมาหรือไม่
    if len(sys.argv) > 1:
        # ถ้ามี argument = ถามคำถามเดียว
        question = " ".join(sys.argv[1:])
        single_question_mode(question)
    else:
        # ถ้าไม่มี = เข้าโหมด interactive
        interactive_mode()

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()