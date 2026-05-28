from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class MemoryConsolidator:
    def __init__(self, threshold: float = 0.45):
        self.threshold = threshold
        self._vectorizer = TfidfVectorizer(use_idf=False)

    def consolidate(self, store) -> dict:
        memories = store.get_all()
        if len(memories) < 2:
            return {"removed": 0, "merged": 0, "kept": len(memories)}

        contents = [m["content"] for m in memories]
        try:
            tfidf_matrix = self._vectorizer.fit_transform(contents)
            sim_matrix = cosine_similarity(tfidf_matrix)
        except ValueError:
            return {"removed": 0, "merged": 0, "kept": len(memories)}

        to_remove: set[int] = set()
        merged_count = 0

        for i in range(len(memories)):
            if i in to_remove:
                continue
            for j in range(i + 1, len(memories)):
                if j in to_remove:
                    continue
                if sim_matrix[i][j] >= self.threshold:
                    winner, loser = self._pick_winner(memories[i], memories[j], i, j)
                    if loser == j:
                        self._merge_into(memories[i], memories[j])
                        to_remove.add(j)
                    else:
                        self._merge_into(memories[j], memories[i])
                        to_remove.add(i)
                    merged_count += 1
                    break

        for idx in sorted(to_remove, reverse=True):
            store.delete(memories[idx]["id"])

        return {"removed": len(to_remove), "merged": merged_count, "kept": len(store)}

    def _pick_winner(self, a: dict, b: dict, idx_a: int, idx_b: int) -> tuple[int, int]:
        len_a = len(a.get("content", ""))
        len_b = len(b.get("content", ""))
        if len_a != len_b:
            return (idx_a, idx_b) if len_a >= len_b else (idx_b, idx_a)
        return (idx_b, idx_a)

    def _merge_into(self, keeper: dict, discard: dict) -> None:
        kept = keeper.get("content", "")
        discarded = discard.get("content", "")
        if discarded not in kept:
            keeper["content"] = kept + "; " + discarded
