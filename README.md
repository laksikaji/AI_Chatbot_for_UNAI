# AI Chatbot for UNAI

AI Chatbot ที่ใช้ Pinecone Assistant สำหรับตอบคำถามจากเอกสารองค์กร

## Features
- 📄 รองรับ PDF และ Google Docs
- 🤖 ตอบคำถามอัตโนมัติจากเอกสาร
- 🔄 อัปเดตเอกสารได้ง่าย
- 🌐 รองรับภาษาไทย

## Prerequisites
- Python 3.8+
- Pinecone API Key
- Google Drive API Credentials

## Installation

1. Clone repository:
\`\`\`bash
git clone <repository-url>
cd AI_Chatbot_UNAI
\`\`\`

2. ติดตั้ง dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. ตั้งค่า environment variables:
   - Copy `.env.example` เป็น `.env`
   - ใส่ Pinecone API key
   - ใส่ Google Drive Folder ID

4. ดาวน์โหลด `credentials.json` จาก Google Cloud Console

## Usage

### Upload เอกสาร:
\`\`\`bash
python upload_documents.py
\`\`\`

### ถามคำถาม:
\`\`\`bash
python chat.py
\`\`\`

## Project Structure
\`\`\`
AI_Chatbot_UNAI/
├── upload_documents.py   # Script สำหรับ upload เอกสาร
├── chat.py              # Script สำหรับถามคำถาม
├── .env                 # Environment variables (ห้าม commit!)
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # Documentation
\`\`\`

## Contributing
1. Fork the project
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License
MIT License

## Author
UNAI Team