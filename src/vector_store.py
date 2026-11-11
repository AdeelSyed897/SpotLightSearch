from pathlib import Path
import lancedb


DB_PATH = "data/vectors"
TABLE_NAME = "chunks"


class VectorStore:
    def __init__(self, db_path=DB_PATH):
        self.db = lancedb.connect(db_path)

        if TABLE_NAME in self.db.table_names():
            self.table = self.db.open_table(TABLE_NAME)
        else:
            self.table = None

    def add_chunks(self,file_path: str,chunks: list[str],vectors: list[list[float]],chunk_ids: list[str]):
        if len(chunks) != len(vectors):
            raise ValueError("Each chunk must have one vector")

        if len(chunks) != len(chunk_ids):
            raise ValueError("Each chunk must have one chunk ID")

        if not chunks:
            return

        if any(len(vector) != 384 for vector in vectors):
            raise ValueError("All vectors must have 384 dimensions")

        file_path = str(Path(file_path).resolve())

        records = []

        for i, (chunk, vector, chunk_id) in enumerate(zip(chunks, vectors, chunk_ids)):

            records.append({
                "chunk_id": chunk_id,
                "file_path": file_path,
                "chunk_index": i,
                "vector": vector
            })

        if self.table is None:
            self.table = self.db.create_table(
                TABLE_NAME,
                data=records
            )
        else:
            # Escape single quotes for the SQL filter
            safe_path = file_path.replace("'", "''")

            self.table.delete(f"file_path = '{safe_path}'")
            self.table.add(records)

    def search(self, query_vector: list[float], limit=5):
        if self.table is None:
            return []

        if len(query_vector) != 384:
            raise ValueError("Query vector must have 384 dimensions")

        return (
            self.table.search(query_vector)
            .distance_type("cosine")
            .limit(limit)
            .to_list()
        )

    def remove_file(self, file_path: str):
        if self.table is None:
            return

        file_path = str(Path(file_path).resolve())
        safe_path = file_path.replace("'", "''")

        self.table.delete(
            f"file_path = '{safe_path}'"
        )
