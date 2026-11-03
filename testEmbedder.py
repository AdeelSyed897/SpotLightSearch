
from src.parser import extract_text
from src.chunker import chunk_text
from src.embedder import Embedder


# Step 1: Extract text
text = extract_text("test_files/sample.txt")

# Step 2: Split into chunks
chunks = chunk_text(text, chunk_size=20, overlap=5)

# Step 3: Generate embeddings
embedder = Embedder()
vectors = embedder.embed_chunks(chunks)

print(f"Number of chunks: {len(chunks)}")
print(f"Number of vectors: {len(vectors)}")

for i, vector in enumerate(vectors):
    print(f"\nChunk {i + 1}: {chunks[i]}")
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")
