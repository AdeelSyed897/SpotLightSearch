from pathlib import Path

from src.parser import extract_text
from src.chunker import chunk_text
from src.embedder import Embedder
from src.sqlite_store import SQLiteStore
from src.vector_store import VectorStore


class Indexer:
    def __init__(self):
        self.embedder = Embedder()
        self.sqlite_store = SQLiteStore()
        self.vector_store = VectorStore()

    def index_file(self, file_path: str):
        path = Path(file_path)

        text = extract_text(path)

        chunks = chunk_text(text, chunk_size=150,overlap=30)

        vectors = self.embedder.embed_chunks(chunks)

        self.sqlite_store.add_chunks(str(path), chunks)

        self.vector_store.add_chunks( str(path), chunks, vectors)

        return len(chunks)