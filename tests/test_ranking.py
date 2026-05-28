import pytest
from datetime import datetime, timezone, timedelta
from memory.ranking.ranker import MemoryRanker


class TestMemoryRanker:
    def test_rerank_empty(self):
        ranker = MemoryRanker()
        assert ranker.rerank([], strategy="hybrid") == []
        assert ranker.rerank([], strategy="semantic") == []
        assert ranker.rerank([], strategy="recency") == []

    def test_semantic_preserves_order(self):
        ranker = MemoryRanker()
        results = [
            {"id": "1", "content": "a", "score": 0.3},
            {"id": "2", "content": "b", "score": 0.9},
            {"id": "3", "content": "c", "score": 0.5},
        ]
        ranked = ranker.rerank(results, strategy="semantic")
        assert ranked[0]["id"] == "2"
        assert ranked[1]["id"] == "3"
        assert ranked[2]["id"] == "1"

    def test_recency_boosts_newer(self):
        ranker = MemoryRanker(recency_halflife=1.0)
        now = datetime.now(timezone.utc)
        results = [
            {"id": "old", "content": "old", "score": 0.5, "created_at": (now - timedelta(days=30)).isoformat()},
            {"id": "new", "content": "new", "score": 0.5, "created_at": now.isoformat()},
        ]
        ranked = ranker.rerank(results, strategy="recency")
        assert ranked[0]["id"] == "new"

    def test_hybrid_combines_scores(self):
        ranker = MemoryRanker(recency_halflife=30.0, recency_weight=0.5)
        now = datetime.now(timezone.utc)
        results = [
            {
                "id": "a", "content": "relevant but old", "score": 0.9,
                "created_at": (now - timedelta(days=60)).isoformat(),
            },
            {
                "id": "b", "content": "less relevant but new", "score": 0.4,
                "created_at": now.isoformat(),
            },
        ]
        ranked = ranker.rerank(results, strategy="hybrid")
        assert len(ranked) == 2
        for m in ranked:
            assert 0 <= m["score"] <= 1

    def test_missing_created_at_uses_default(self):
        ranker = MemoryRanker()
        results = [
            {"id": "1", "content": "test", "score": 0.7},
        ]
        ranked = ranker.rerank(results, strategy="hybrid")
        assert len(ranked) == 1
        assert 0 < ranked[0]["score"] < 1

    def test_unknown_strategy_raises(self):
        ranker = MemoryRanker()
        with pytest.raises(ValueError, match="Unknown strategy"):
            ranker.rerank([{"id": "1", "content": "x", "score": 0.5}], strategy="invalid")
