from core import DatabaseManager
from pathlib import Path

db = DatabaseManager(Path("data/database"))
results = db.collection.get(where={"filename": "lab_report_blood.txt"})

print(f"Chunks for lab_report_blood.txt: {len(results['ids'])}")
for meta, text in zip(results['metadatas'], results['documents']):
    print("-" * 40)
    print(f"Chunk ID: {meta.get('chunk_id')}")
    print(f"TEXT:\n{text}")
