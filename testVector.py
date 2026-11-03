
from src.parser import extract_text
from src.chunker import chunk_text
from src.embedder import Embedder
from src.vector_store import VectorStore


# Extract and chunk
text = extract_text("test_files/sample.txt")
chunks = chunk_text(text, chunk_size=20, overlap=5)

# Generate embeddings
embedder = Embedder()
vectors = embedder.embed_chunks(chunks)

# Store in LanceDB
store = VectorStore()

store.add_chunks(
    "test_files/sample.txt",
    chunks,
    vectors
)

print(f"Stored {len(vectors)} vectors!")

# Semantic search
query = "How does the system search documents by meaning?"

query_vector = embedder.embed_chunks([query])[0]

results = store.search(query_vector)

print("\nSEMANTIC SEARCH RESULTS:")

for result in results:
    print(f"\nFile: {result['file_path']}")
    print(f"Chunk: {result['chunk_index']}")
    print(f"Distance: {result['_distance']:.4f}")
    print(f"Chunk ID: {result['chunk_id']}")
