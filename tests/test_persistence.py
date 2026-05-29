import pytest
import os
import tempfile
from memory.ingestion.memory_store import MemoryStore


class TestPersistence:
    def test_save_and_load(self):
        path = os.path.join(tempfile.gettempdir(), "test_memories.json")
        store = MemoryStore()
        store.add("memory one")
        store.add("memory two", {"cat": "test"})
        store.save(path)
        assert os.path.exists(path)

        store2 = MemoryStore(filepath=path)
        assert len(store2) == 2
        assert store2.get_all()[0]["content"] == "memory one"
        assert store2.get_all()[1]["metadata"]["cat"] == "test"

        os.remove(path)

    def test_auto_load_on_init(self):
        path = os.path.join(tempfile.gettempdir(), "test_auto.json")
        store = MemoryStore()
        store.add("auto load test")
        store.save(path)

        store2 = MemoryStore(filepath=path)
        assert len(store2) == 1
        assert store2.get_all()[0]["content"] == "auto load test"

        os.remove(path)

    def test_auto_save_on_add(self):
        path = os.path.join(tempfile.gettempdir(), "test_autosave.json")
        store = MemoryStore(filepath=path)
        store.add("autosave content")

        store2 = MemoryStore(filepath=path)
        assert len(store2) == 1
        assert store2.get_all()[0]["content"] == "autosave content"

        os.remove(path)

    def test_auto_save_on_delete(self):
        path = os.path.join(tempfile.gettempdir(), "test_delsave.json")
        store = MemoryStore(filepath=path)
        sid = store.add("keep")
        store.add("remove")
        store.delete(sid)
        assert len(store) == 1

        store2 = MemoryStore(filepath=path)
        assert len(store2) == 1
        assert store2.get_all()[0]["content"] == "remove"

        os.remove(path)

    def test_auto_save_on_clear(self):
        path = os.path.join(tempfile.gettempdir(), "test_clearsave.json")
        store = MemoryStore(filepath=path)
        store.add("will be cleared")
        store.clear()

        store2 = MemoryStore(filepath=path)
        assert len(store2) == 0

        os.remove(path)

    def test_nonexistent_file_no_error(self):
        path = os.path.join(tempfile.gettempdir(), "nonexistent_file.json")
        try:
            os.remove(path)
        except OSError:
            pass
        store = MemoryStore(filepath=path)
        assert len(store) == 0
