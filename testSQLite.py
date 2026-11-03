from src.parser import extract_text
from src.chunker import chunk_text
from src.sqlite_store import SQLiteStore


# Extract text from document
text = extract_text("test_files/sample.txt")

# Split into chunks
chunks = chunk_text(text, chunk_size=20, overlap=5)

# Store chunks in SQLite
store = SQLiteStore()
store.add_chunks("test_files/sample.txt", chunks)

print(f"Stored {len(chunks)} chunks!")

# Test keyword search
results = store.search("SQLite")

print("\nSEARCH RESULTS:")

for path, index, content, score in results:
    print(f"\nFile: {path}")
    print(f"Chunk: {index}")
    print(f"BM25 Score: {score:.6f}")
    print(f"Content: {content}")

store.close()
