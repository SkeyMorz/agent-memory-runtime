import numpy as np


class EmbeddingRetriever:
    def __init__(self, store, model_name: str = "all-MiniLM-L6-v2"):
        self.store = store
        self.model_name = model_name
        self._model = None
        self._embeddings: list[np.ndarray] | None = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _build_index(self) -> None:
        memories = self.store.get_all()
        if not memories:
            self._embeddings = []
            return
        contents = [m["content"] for m in memories]
        self._embeddings = self.model.encode(
            contents, convert_to_numpy=True, show_progress_bar=False
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        memories = self.store.get_all()
        if not memories:
            return []

        self._build_index()
        query_vec = self.model.encode(
            [query], convert_to_numpy=True, show_progress_bar=False
        )[0]

        scores = np.dot(self._embeddings, query_vec) / (
            np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(query_vec)
        )

        ranked = np.argsort(scores)[::-1]
        results = []
        for idx in ranked[:top_k]:
            if scores[idx] > 0:
                m = dict(memories[idx])
                m["score"] = float(scores[idx])
                results.append(m)
        return results
