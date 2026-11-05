import sqlite3
from pathlib import Path


DB_PATH = Path("data/spotlight.db")


class SQLiteStore:
    def __init__(self, db_path=DB_PATH):
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path)

        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
            USING fts5(
                chunk_id UNINDEXED,
                file_path UNINDEXED,
                chunk_index UNINDEXED,
                content
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS indexed_files (
                file_path TEXT PRIMARY KEY,
                mtime_ns INTEGER NOT NULL
            )
        """)

        self.conn.commit()

    def add_chunks(self, file_path: str, chunks: list[str], chunk_ids: list[str]):
        if len(chunks) != len(chunk_ids):
            raise ValueError("Each chunk must have one chunk ID")

        file_path = str(Path(file_path).resolve())

        with self.conn:
            # Replace existing chunks for this file
            self.conn.execute(
                "DELETE FROM chunks_fts WHERE file_path = ?",
                (file_path,)
            )

            for i, (chunk, chunk_id) in enumerate(zip(chunks, chunk_ids)):

                self.conn.execute("""
                    INSERT INTO chunks_fts
                    (chunk_id, file_path, chunk_index, content)
                    VALUES (?, ?, ?, ?)
                """, (chunk_id, file_path, i, chunk))


    # setter for file and modification time
    def set_file_mtime(self, file_path: str, mtime_ns: int):
        file_path = str(Path(file_path).resolve())

        with self.conn:
            self.conn.execute("""
                INSERT INTO indexed_files (file_path, mtime_ns)
                VALUES (?, ?)
                ON CONFLICT(file_path)
                DO UPDATE SET mtime_ns = excluded.mtime_ns
            """, (file_path, mtime_ns))

    # return modification time of file
    def get_file_mtime(self, file_path: str):
        file_path = str(Path(file_path).resolve())

        cursor = self.conn.execute("""
            SELECT mtime_ns
            FROM indexed_files
            WHERE file_path = ?
        """, (file_path,))

        row = cursor.fetchone()

        if row is None:
            return None

        return row[0]

    def search(self, query: str):
        cursor = self.conn.execute("""
            SELECT
                file_path,
                chunk_index,
                content,
                bm25(chunks_fts) AS score
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY score
            LIMIT 5
        """, (query,))

        return cursor.fetchall()

    def close(self):
        self.conn.close()
