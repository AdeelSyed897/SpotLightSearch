
from src.sqlite_store import SQLiteStore

store = SQLiteStore()

results = store.search("semantic")

for path, index, content, score in results:
    print(f"File: {path}")
    print(f"Chunk: {index}")
    print(f"Text: {content}")
    print()

store.close()
