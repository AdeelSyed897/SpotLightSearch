
from src.embedder import Embedder
from src.vector_store import VectorStore

embedder = Embedder()
store = VectorStore()

query = "Finding information based on meaning"

vector = embedder.embed_chunks([query])[0]

results = store.search(vector)

for result in results:
    print(result["file_path"])
    print("Chunk:", result["chunk_index"])
    print("Distance:", result["_distance"])
    print()
