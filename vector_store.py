
import faiss
from sentence_transformers import SentenceTransformer


class VectorStore:
    """Semantic search for one uploaded PDF."""

    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def build(self, chunks: list[dict]) -> None:
        if not chunks:
            raise ValueError("No text chunks available.")

        self.chunks = chunks
        texts = [chunk["text"] for chunk in chunks]

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")

        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    def search(
        self,
        question: str,
        top_k: int = 4
    ) -> list[dict]:
        if self.index is None:
            raise RuntimeError("Build the index before searching.")

        query_vector = self.model.encode(
            [question],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")

        k = min(top_k, len(self.chunks))
        scores, ids = self.index.search(query_vector, k)

        results = []

        for score, idx in zip(scores[0], ids[0]):
            if idx >= 0:
                item = dict(self.chunks[int(idx)])
                item["score"] = float(score)
                results.append(item)

        return results
