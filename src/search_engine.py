from src.embedder import Embedder
from src.sqlite_store import SQLiteStore
from src.vector_store import VectorStore
import time
import math

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

    #convert into recency score with a logarithmic decay
    def _recency_score(self, mtime_ns: int) -> float:
        current_time_ns = time.time_ns()

        age_ns = max(0, current_time_ns - mtime_ns)

        nanoseconds_per_day = 86_400_000_000_000
        age_days = age_ns / nanoseconds_per_day

        half_life_days = 180

        return math.exp(
            -math.log(2) * age_days / half_life_days
        )