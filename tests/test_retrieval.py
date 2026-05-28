import pytest
from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever


class TestMemoryRetriever:
    def test_search_returns_relevant_results(self):
        store = MemoryStore()
        store.add("User likes Japanese food")
        store.add("User works as a Python developer")
        store.add("User lives in Tokyo")

        retriever = MemoryRetriever(store)
        results = retriever.search("food preferences", top_k=2)

        assert len(results) > 0
        assert any("food" in r["content"].lower() for r in results)

    def test_search_empty_store(self):
        store = MemoryStore()
        retriever = MemoryRetriever(store)
        results = retriever.search("anything")
        assert results == []

    def test_search_respects_top_k(self):
        store = MemoryStore()
        for i in range(10):
            store.add(f"Memory {i}")

        retriever = MemoryRetriever(store)
        results = retriever.search("memory", top_k=3)
        assert len(results) <= 3

    def test_results_have_scores(self):
        store = MemoryStore()
        store.add("Test memory content")

        retriever = MemoryRetriever(store)
        results = retriever.search("test", top_k=1)

        assert len(results) == 1
        assert "score" in results[0]
        assert results[0]["score"] > 0
