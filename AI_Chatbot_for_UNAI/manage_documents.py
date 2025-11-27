import os
import requests
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
ASSISTANT_NAME = os.getenv('ASSISTANT_NAME', 'unai-chatbot')

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def get_base_url():
    return f"https://prod-1-data.ke.pinecone.io/assistant/files/{ASSISTANT_NAME}"

def get_headers():
    return {"Api-Key": PINECONE_API_KEY}

def list_files():
    url = get_base_url()
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        # The API returns {"files": [...]}
        return response.json().get('files', [])
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def delete_file(file_id):
    url = f"{get_base_url()}/{file_id}"
    try:
        response = requests.delete(url, headers=get_headers())
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error deleting file {file_id}: {e}")
        return False

def main():
    print_header("Pinecone Document Manager")
    
    if not PINECONE_API_KEY:
        print("Error: PINECONE_API_KEY not found.")
        return

    while True:
        print("Fetching file list...")
        files = list_files()
        
        if not files:
            print("No files found in Assistant.")
        else:
            print(f"Found {len(files)} files in assistant '{ASSISTANT_NAME}':")
            print("-" * 60)
            print(f"{'No.':<5} {'ID':<40} {'Name'}")
            print("-" * 60)
            for idx, f in enumerate(files, 1):
                print(f"{idx:<5} {f.get('id'):<40} {f.get('name')}")
            print("-" * 60)
        
        print("\nOptions:")
        print("  [Number] Delete specific file (e.g., 1)")
        print("  [A]      Delete ALL files")
        print("  [R]      Refresh list")
        print("  [Q]      Quit")
        
        choice = input("\nEnter choice: ").strip().lower()
        
        if choice in ['q', 'quit', 'exit']:
            print("\nGoodbye!")
            break
        elif choice == 'r':
            continue
        elif choice == 'a':
            if not files:
                print("\nNothing to delete.")
                input("Press Enter to continue...")
                continue
                
            confirm = input("\n⚠️  Are you sure you want to delete ALL files? (yes/no): ")
            if confirm.lower() == 'yes':
                for f in files:
                    print(f"Deleting {f.get('name')}...", end=' ')
                    if delete_file(f.get('id')):
                        print("✅ Done")
                    else:
                        print("❌ Failed")
                print("\nAll operations completed.")
                input("Press Enter to continue...")
        else:
            try:
                idx = int(choice)
                if 1 <= idx <= len(files):
                    file_to_delete = files[idx-1]
                    confirm = input(f"\nDelete '{file_to_delete.get('name')}'? (y/n): ")
                    if confirm.lower() == 'y':
                        print(f"Deleting...", end=' ')
                        if delete_file(file_to_delete.get('id')):
                            print("✅ Deleted successfully.")
                        else:
                            print("❌ Deletion failed.")
                        input("Press Enter to continue...")
                else:
                    print("\n❌ Invalid number.")
                    input("Press Enter to continue...")
            except ValueError:
                print("\n❌ Invalid input.")
                input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted.")
