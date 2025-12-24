from core import DatabaseManager
from pathlib import Path

DB_DIR = Path("data/database")
db = DatabaseManager(DB_DIR)

print(f"Total documents in DB: {db.get_count()}")

query = "What specific error happened on Port 80?"
print(f"\nQuerying for: '{query}'")
results = db.query(query, n_results=5)

if not results:
    print("No results found.")
else:
    print(f"Found {len(results)} chunks:")
    for i, chunk in enumerate(results):
        print(f"--- Chunk {i+1} ---")
        print(f"File: {chunk['filename']}")
        print(f"Distance: {chunk.get('distance')}")
        print(f"Text snippet: {chunk['text'][:100]}...")
