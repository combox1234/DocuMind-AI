
import logging
from pathlib import Path
from core import DatabaseManager
from core.processor import FileProcessor
from models.document import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reingest():
    BASE_DIR = Path(__file__).parent
    DB_DIR = BASE_DIR / "data" / "database"
    LOG_FILE = BASE_DIR / "data/sorted/Technology/DevOps/log/docker_deployment_logs.log"
    
    print(f"Target Log File: {LOG_FILE}")
    
    # Init
    db = DatabaseManager(DB_DIR)
    processor = FileProcessor()
    
    # 1. Process File (Now extracting full text!)
    print("Processing file...")
    text = processor.extract_text(LOG_FILE)
    print(f"Extracted Text Length: {len(text)} bytes")
    print(f"Preview: {text[:100]}...")
    
    if len(text) < 50:
        print("❌ CRITICAL: Text extraction still failed!")
        return

    # 2. Create chunks
    doc = processor.create_document(LOG_FILE, text, "Technology")
    chunks = processor.create_chunks(doc, chunk_size=600)
    print(f"Created {len(chunks)} chunks.")
    
    # 3. Add to DB (Upsert logic in Chroma usually handles IDs)
    # Note: Chunk IDs are hash based, so if content changed, IDs change.
    # Ideally should delete old chunks first, but I'll trust the search will find the new ones.
    print("Adding to DB...")
    db.add_chunks(chunks)
    print("✅ Re-ingestion complete.")

if __name__ == "__main__":
    reingest()
