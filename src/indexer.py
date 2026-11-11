from pathlib import Path
from src.parser import extract_text
from src.parser import is_supported_file
from src.chunker import chunk_text
from src.embedder import Embedder
from src.sqlite_store import SQLiteStore
from src.vector_store import VectorStore
import uuid

IGNORED_DIRECTORIES = {".git", ".venv","venv","node_modules","__pycache__",}
TIER_1_MAX_CHUNKS = 250
TIER_2_MAX_CHUNKS = 1000
TIER_2_SAMPLE_SIZE = 250
class Indexer:
    def __init__(self):
        self.embedder = Embedder()
        self.sqlite_store = SQLiteStore()
        self.vector_store = VectorStore()

    def index_file(self, file_path: str):
        path = Path(file_path).expanduser().resolve()

        current_mtime = path.stat().st_mtime_ns
        stored_mtime = self.sqlite_store.get_file_mtime(str(path))

        if stored_mtime == current_mtime:
            print(f"Skipping unchanged file: {path}")
            return 0

        # Always index the filename
        self.sqlite_store.add_file(str(path))

        # Parse + chunk so we can determine the tier
        text = extract_text(path)

        chunks = chunk_text(
            text,
            chunk_size=150,
            overlap=30
        )

        tier = self._determine_tier(len(chunks))

        print(
            f"Tier {tier}: {path} "
            f"({len(chunks)} total chunks)"
        )

        if tier == 1:
            indexed_count = self._index_tier_1(
                path,
                chunks
            )

        elif tier == 2:
            indexed_count = self._index_tier_2(
                path,
                chunks
            )

        else:
            indexed_count = self._index_tier_3(
                path
            )

        # Only mark the file as finished after indexing succeeds
        self.sqlite_store.set_file_mtime(
            str(path),
            current_mtime
        )

        return indexed_count

    def index_directory(self, directory_path: str):
        root = Path(directory_path).expanduser()

        if not root.is_dir():
            raise NotADirectoryError(f"Directory not found: {root}")

        for path in root.rglob("*"):

            if any(part in IGNORED_DIRECTORIES for part in path.parts):
                continue

            if path.is_file() and is_supported_file(path):
                print(f"Indexing: {path}")
                self.index_file(path)

    def _determine_tier(self, chunk_count: int) -> int:
        if chunk_count <= TIER_1_MAX_CHUNKS:
            return 1

        if chunk_count <= TIER_2_MAX_CHUNKS:
            return 2

        return 3


    def _index_tier_1(self, path: Path, chunks: list[str]):
        indexed_chunks = list(enumerate(chunks))

        selected_chunks = [
            chunk
            for original_index, chunk in indexed_chunks
        ]
        chunk_ids = [
            str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"{path}:{original_index}"
                )
            )
            for original_index, chunk in indexed_chunks
        ]

        vectors = self.embedder.embed_chunks(selected_chunks)

        self.sqlite_store.add_chunks(
            str(path),
            selected_chunks,
            chunk_ids
        )

        self.vector_store.add_chunks(
            str(path),
            selected_chunks,
            vectors,
            chunk_ids
        )

        return len(selected_chunks)


    def _index_tier_2(self, path: Path, chunks: list[str]):
        indexed_chunks = self._sample_chunks(
            chunks,
            TIER_2_SAMPLE_SIZE
        )

        selected_chunks = [
            chunk
            for original_index, chunk in indexed_chunks
        ]

        chunk_ids = [
            str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"{path}:{original_index}"
                )
            )
            for original_index, chunk in indexed_chunks
        ]

        vectors = self.embedder.embed_chunks(selected_chunks)

        self.sqlite_store.add_chunks(
            str(path),
            selected_chunks,
            chunk_ids
        )

        self.vector_store.add_chunks(
            str(path),
            selected_chunks,
            vectors,
            chunk_ids
        )

        return len(selected_chunks)


    def _index_tier_3(self, path: Path):
        self.sqlite_store.add_chunks(
            str(path),
            [],
            []
        )

        self.vector_store.remove_file(
            str(path)
        )

        return 0


    def _sample_chunks(
        self,
        chunks: list[str],
        sample_size: int
    ) -> list[tuple[int, str]]:

        if len(chunks) <= sample_size:
            return list(enumerate(chunks))

        sampled = []

        for i in range(sample_size):
            index = round(
                i * (len(chunks) - 1) / (sample_size - 1)
            )

            sampled.append(
                (index, chunks[index])
            )

        return sampled