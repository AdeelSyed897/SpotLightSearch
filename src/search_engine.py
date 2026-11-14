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

    def _semantic_relevance(self,semantic: float,filename: float,recency: float,multi_chunk: float) -> float:
        return 0.55 * semantic + 0.20 * filename + 0.15 * recency + 0.10 * multi_chunk
    
    #convert into recency score with a exp decay
    def _recency_score(self, mtime_ns: int) -> float:
        current_time_ns = time.time_ns()

        age_ns = max(0, current_time_ns - mtime_ns)

        nanoseconds_per_day = 86_400_000_000_000
        age_days = age_ns / nanoseconds_per_day

        half_life_days = 180

        return math.exp(-math.log(2) * age_days / half_life_days)

    def _normalize_semantic(self, distance: float) -> float:
        return max(0.0, min(1.0, 1.0 - distance))

    def _normalize_bm25(self, scores: list[float]) -> list[float]:
        if not scores:
            return []

        best = min(scores)
        worst = max(scores)

        if best == worst:
            return [1.0] * len(scores)

        return [(worst - score) / (worst - best) for score in scores]

    def _multi_chunk_score(self, chunk_scores: list[float]) -> float:
        if not chunk_scores:
            return 0.0

        strong_chunks = sum(1 for score in chunk_scores if score >= 0.6)

        return min(1.0, strong_chunks / 4)