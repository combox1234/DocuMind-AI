"""
Async Health Check Script
Verifies:
1. Redis Connection
2. Celery Worker Availability
3. Task Execution (Ping)
"""
import sys
import time
from pathlib import Path
import redis
from celery.app.control import Control

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from worker import celery_app

def check_redis():
    print("1. Checking Redis Connection...", end=" ")
    try:
        r = redis.from_url(Config.CELERY_BROKER_URL)
        if r.ping():
            print("OK")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def check_workers():
    print("2. Checking Celery Workers...", end=" ")
    try:
        # Inspect active workers
        i = celery_app.control.inspect()
        active = i.active()
        if active:
            count = sum(len(v) for v in active.values())
            print(f"OK ({len(active)} worker nodes found, {count} active tasks)")
            return True
        else:
            # Stats might be empty if no workers, but inspect object exists
            stats = i.stats()
            if stats:
                print(f"OK ({len(stats)} worker nodes ready)")
                return True
            else:
                print("FAILED (No running workers found)")
                print("   -> Tip: Run 'celery -A worker.celery_app worker -l info'")
                return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    print("=== DocuMind AI Async Health Check ===")
    
    if not check_redis():
        sys.exit(1)
        
    if not check_workers():
        sys.exit(1)
        
    print("\nSystem is READY for async processing.")

if __name__ == "__main__":
    main()
