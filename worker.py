import os
import logging
from pathlib import Path
from celery import Celery
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core modules
from config import Config
from core import DatabaseManager, LLMService, FileProcessor
from models import Document

# Initialize Celery
celery_app = Celery('documind_worker', broker=Config.CELERY_BROKER_URL)
celery_app.conf.update(
    result_backend=Config.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Initialize Services (Lazy loading to avoid fork issues)
db_manager = None
llm_service = None
file_processor = None

def get_services():
    """Lazy load services to ensure connection safety in workers"""
    global db_manager, llm_service, file_processor
    if db_manager is None:
        db_manager = DatabaseManager(Config.DB_DIR)
    if llm_service is None:
        llm_service = LLMService(model=Config.LLM_MODEL)
    if file_processor is None:
        file_processor = FileProcessor()
    return db_manager, llm_service, file_processor

@celery_app.task(bind=True, name='worker.process_file_task')
def process_file_task(self, filepath_str):
    """
    Celery task to process a file asynchronously.
    """
    filepath = Path(filepath_str)
    logger.info(f"🚀 [Worker] Picking up task for: {filepath.name}")
    
    # Get services
    db, llm, processor = get_services()
    
    try:
        # Check existence
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return {"status": "failed", "reason": "File not found"}

        # 1. Extract Text
        text = processor.extract_text(filepath)
        if not text:
            text = f"File: {filepath.name}"
        
        # 2. Classify
        hierarchy = llm.classify_hierarchical(text, filepath.name)
        domain = hierarchy["domain"]
        category = hierarchy["category"]
        file_ext = hierarchy["file_extension"]
        
        # 3. Create Document
        document = processor.create_document(filepath, text, domain)
        
        # 4. Move to Sorted Directory
        category_dir = Config.SORTED_DIR / domain / category / file_ext
        category_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = category_dir / filepath.name
        
        # Handle duplicates
        if dest_path.exists():
            base_stem = filepath.stem
            suffix = filepath.suffix
            counter = 2
            while dest_path.exists():
                dest_path = category_dir / f"{base_stem}_{counter}{suffix}"
                counter += 1
        
        shutil.move(str(filepath), str(dest_path))
        document.filepath = dest_path # Update path
        
        # 5. Create Chunks
        chunks = processor.create_chunks(document, chunk_size=600)
        
        # 6. Store in Database
        if chunks:
            db.add_chunks(chunks)
            logger.info(f"✅ [Worker] Processed {len(chunks)} chunks for {filepath.name}")
            return {
                "status": "success", 
                "filename": filepath.name, 
                "chunks": len(chunks),
                "destination": str(dest_path)
            }
        
    except Exception as e:
        logger.error(f"❌ [Worker] Error processing {filepath.name}: {e}")
        return {"status": "error", "error": str(e)}

    return {"status": "success", "message": "Processed but no chunks created"}
