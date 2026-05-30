import pytest
from memory.ingestion.memory_store import MemoryStore
from memory.consolidation.consolidator import MemoryConsolidator


class TestMemoryConsolidator:
    def test_consolidate_empty_store(self):
        store = MemoryStore()
        consolidator = MemoryConsolidator()
        result = consolidator.consolidate(store)
        assert result == {"removed": 0, "merged": 0, "kept": 0}

    def test_consolidate_single_memory(self):
        store = MemoryStore()
        store.add("Only memory")
        consolidator = MemoryConsolidator()
        result = consolidator.consolidate(store)
        assert result["kept"] == 1
        assert result["removed"] == 0

    def test_consolidate_merges_similar(self):
        store = MemoryStore()
        store.add("User likes Japanese food, especially ramen and sushi")
        store.add("User loves Japanese cuisine like ramen")
        consolidator = MemoryConsolidator(threshold=0.4)
        result = consolidator.consolidate(store)
        assert result["removed"] >= 1
        assert len(store) == 1

    def test_consolidate_keeps_different(self):
        store = MemoryStore()
        store.add("User likes Japanese food")
        store.add("User is a Python developer")
        store.add("User lives in Tokyo")
        consolidator = MemoryConsolidator(threshold=0.4)
        result = consolidator.consolidate(store)
        assert result["kept"] == 3
        assert result["removed"] == 0

    def test_high_threshold_preserves_more(self):
        store = MemoryStore()
        store.add("User likes Japanese food")
        store.add("User enjoys Japanese meals")
        consolidator = MemoryConsolidator(threshold=0.99)
        result = consolidator.consolidate(store)
        assert result["kept"] == 2

    def test_low_threshold_merges_more(self):
        store = MemoryStore()
        store.add("User likes Japanese food especially ramen")
        store.add("User loves Japanese food like ramen")
        consolidator = MemoryConsolidator(threshold=0.1)
        result = consolidator.consolidate(store)
        assert result["removed"] == 1
        assert len(store) == 1

    def test_merge_preserves_longer_content(self):
        store = MemoryStore()
        shorter_id = store.add("Japanese food")
        longer_id = store.add("User really enjoys Japanese food especially ramen and sushi")
        consolidator = MemoryConsolidator(threshold=0.45)
        consolidator.consolidate(store)
        remaining = store.get_all()
        assert len(remaining) == 1
        assert remaining[0]["id"] == longer_id

    def test_merge_combines_non_overlapping_content(self):
        store = MemoryStore()
        store.add("User likes Japanese food especially ramen")
        store.add("User likes Japanese food and also enjoys sushi")
        consolidator = MemoryConsolidator(threshold=0.55)
        consolidator.consolidate(store)
        remaining = store.get_all()
        assert len(remaining) == 1
        assert "sushi" in remaining[0]["content"]
