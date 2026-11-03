from fastembed import TextEmbedding


MODEL_NAME = "BAAI/bge-small-en-v1.5"


class Embedder:
    def __init__(self):
        self.model = TextEmbedding(model_name=MODEL_NAME)

    def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        if not chunks:
            return []

        embeddings = self.model.embed(chunks)

        return [vector.tolist() for vector in embeddings]
