"""
Universal RAG System - File Watcher (Async Frontend)
Dispatches tasks to Celery worker for processing.
"""

import time
import logging
from pathlib import Path
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

from core import DatabaseManager
from config import Config
from worker import process_file_task

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
INCOMING_DIR = Config.INCOMING_DIR
SORTED_DIR = Config.SORTED_DIR
DB_DIR = Config.DB_DIR

# Files to skip
SKIP_FILES = {
    'index.html', 'index_backup.html', 'index_backup_2.html', '.gitignore', '.env',
    'config.py', 'setup.py', 'requirements.txt', 'watcher.py', 'app.py', 'cleanup.py', 'worker.py'
}
SKIP_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.sh', '.bat'}

def should_skip_file(filepath: Path) -> bool:
    """Check if file should be skipped"""
    if filepath.name in SKIP_FILES:
        return True
    if filepath.suffix.lower() in SKIP_EXTENSIONS:
        return True
    if filepath.name.startswith('.'):
        return True
    return False

# Ensure directories exist
INCOMING_DIR.mkdir(parents=True, exist_ok=True)
SORTED_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Initialize only DB Manager for cleanup/sync (Processing is done by Worker)
db_manager = DatabaseManager(DB_DIR)

def process_file(filepath):
    """Dispatch file processing task to Celery worker"""
    filepath = Path(filepath)
    
    if not filepath.exists() or not filepath.is_file():
        return
    
    if should_skip_file(filepath):
        logger.info(f"⊘ Skipped (blacklist): {filepath.name}")
        return
    
    logger.info(f"📤 [Watcher] Queuing file: {filepath.name}")
    try:
        # ASYNC CALL using Celery
        process_file_task.delay(str(filepath))
        logger.info(f"✅ [Watcher] Task queued for {filepath.name}")
    except Exception as e:
        logger.error(f"❌ [Watcher] Failed to queue task: {e}")

def remove_file_from_db(filepath):
    """Remove file vectors from database when file is deleted"""
    filepath = Path(filepath)
    try:
        # Remove by filepath from DB
        deleted_count = db_manager.delete_by_filepath(str(filepath))
        logger.info(f"Removed {deleted_count} chunks from database for {filepath.name}")
    except Exception as e:
        logger.error(f"Error removing file from database: {e}")

class FileWatcherHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def on_created(self, event):
        time.sleep(1) # Debounce
        if event.is_directory:
            logger.info(f"New folder detected: {event.src_path}")
            process_folder_recursive(event.src_path)
        else:
            logger.info(f"New file detected: {event.src_path}")
            process_file(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")
            remove_file_from_db(event.src_path)

def process_folder_recursive(folder_path):
    """Recursively queue all files in a folder"""
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        return
    
    logger.info(f"Scanning folder: {folder_path}")
    for item in folder_path.rglob('*'):
        if item.is_file():
            process_file(item)

def process_existing_files():
    """Queue existing files"""
    logger.info("Checking for existing files...")
    for item in INCOMING_DIR.iterdir():
        if item.is_file():
            process_file(item)
        elif item.is_dir():
            process_folder_recursive(item)

def sync_sorted_with_db():
    """Clean up dangling DB entries"""
    try:
        results = db_manager.collection.get()
        ids = results.get('ids', [])
        metadatas = results.get('metadatas', [])
        to_delete = []
        for i, meta in enumerate(metadatas):
            fp = meta.get('filepath')
            if fp and not Path(fp).exists():
                to_delete.append(ids[i])
        if to_delete:
            db_manager.collection.delete(ids=to_delete)
            logger.info(f"Pruned {len(to_delete)} dangling chunks")
    except Exception as e:
        logger.error(f"Error during sync: {e}")

def start_watching():
    """Start the file watcher"""
    logger.info("=" * 60)
    logger.info("DocuMind AI - Async Watcher Started")
    logger.info("=" * 60)
    logger.info(f"Incoming: {INCOMING_DIR}")
    
    process_existing_files()
    sync_sorted_with_db()
    
    event_handler = FileWatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INCOMING_DIR), recursive=True)
    observer.start()
    
    logger.info("✓ Watcher active. Waiting for files...")
    try:
        while True:
            sync_sorted_with_db()
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
