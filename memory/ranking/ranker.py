from datetime import datetime, timezone, timedelta
import math


class MemoryRanker:
    def __init__(self, recency_halflife: float = 7.0, recency_weight: float = 0.3):
        self.recency_halflife = recency_halflife
        self.recency_weight = recency_weight

    def rerank(self, results: list[dict], strategy: str = "hybrid") -> list[dict]:
        if not results:
            return []

        if strategy == "semantic":
            return sorted(results, key=lambda m: m.get("score", 0), reverse=True)

        if strategy == "recency":
            reranked = []
            for m in results:
                m = dict(m)
                m["score"] = self._recency_score(m)
                reranked.append(m)
            return sorted(reranked, key=lambda m: m["score"], reverse=True)

        if strategy == "hybrid":
            reranked = []
            for m in results:
                m = dict(m)
                semantic = m.get("score", 0)
                recency = self._recency_score(m)
                m["score"] = (1 - self.recency_weight) * semantic + self.recency_weight * recency
                m["score"] = round(m["score"], 4)
                reranked.append(m)
            return sorted(reranked, key=lambda m: m["score"], reverse=True)

        raise ValueError(f"Unknown strategy: {strategy}")

    def _recency_score(self, memory: dict) -> float:
        created = memory.get("created_at")
        if not created:
            return 0.5
        try:
            dt = datetime.fromisoformat(created)
            now = datetime.now(timezone.utc)
            age_days = (now - dt).total_seconds() / 86400
            return math.exp(-math.log(2) * age_days / self.recency_halflife)
        except (ValueError, TypeError):
            return 0.5
