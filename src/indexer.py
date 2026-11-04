from pathlib import Path
from src.parser import extract_text
from src.parser import is_supported_file
from src.chunker import chunk_text
from src.embedder import Embedder
from src.sqlite_store import SQLiteStore
from src.vector_store import VectorStore
import uuid


class Indexer:
    def __init__(self):
        self.embedder = Embedder()
        self.sqlite_store = SQLiteStore()
        self.vector_store = VectorStore()

    def index_file(self, file_path: str):
        path = Path(file_path)

        text = extract_text(path)

        chunks = chunk_text(text, chunk_size=150,overlap=30)
        chunk_ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{path.resolve()}:{i}"))for i in range(len(chunks))]

        vectors = self.embedder.embed_chunks(chunks)

        self.sqlite_store.add_chunks(str(path), chunks, chunk_ids)

        self.vector_store.add_chunks( str(path), chunks, vectors, chunk_ids)

        return len(chunks)

    def index_directory(self, directory_path: str):
        root = Path(directory_path).expanduser()

        if not root.is_dir():
            raise NotADirectoryError(f"Directory not found: {root}")

        for path in root.rglob("*"):
            if path.is_file() and is_supported_file(path):
                self.index_file(path)