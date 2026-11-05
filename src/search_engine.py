from src.embedder import Embedder
from src.sqlite_store import SQLiteStore
from src.vector_store import VectorStore


class SearchEngine:
    def __init__(self):
        self.embedder = Embedder()
        self.sqlite_store = SQLiteStore()
        self.vector_store = VectorStore()

    def semantic_search(self, query: str, limit=3):
        query_vector = self.embedder.embed_chunks([query])[0]

        results = self.vector_store.search(query_vector,limit=20)

        return self._unique_files([result["file_path"] for result in results],limit)

    def keyword_search(self, query: str, limit=3):
        results = self.sqlite_store.search(query,limit=20)

        return self._unique_files([result[0] for result in results], limit)

    def _unique_files(self, paths: list[str], limit: int):
        unique = []

        for path in paths:
            if path not in unique:
                unique.append(path)

            if len(unique) == limit:
                break

        return unique