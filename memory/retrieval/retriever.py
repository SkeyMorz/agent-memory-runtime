from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class MemoryRetriever:
    def __init__(self, store):
        self.store = store
        self._vectorizer = TfidfVectorizer(stop_words="english")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        memories = self.store.get_all()
        if not memories:
            return []

        contents = [m["content"] for m in memories]
        try:
            tfidf_matrix = self._vectorizer.fit_transform([query] + contents)
            query_vec = tfidf_matrix[0:1]
            doc_vecs = tfidf_matrix[1:]
            scores = cosine_similarity(query_vec, doc_vecs).flatten()
        except ValueError:
            return []

        ranked = np.argsort(scores)[::-1]
        results = []
        for idx in ranked[:top_k]:
            if scores[idx] > 0:
                m = dict(memories[idx])
                m["score"] = float(scores[idx])
                results.append(m)
        return results
