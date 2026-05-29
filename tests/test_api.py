import pytest
from fastapi.testclient import TestClient
from memory.api import app, store


@pytest.fixture(autouse=True)
def clear_store():
    store.clear()
    yield
    store.clear()


client = TestClient(app)


class TestMemoryAPI:
    def test_add_memory(self):
        resp = client.post("/memory", json={"content": "User likes ramen"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "User likes ramen"
        assert "id" in data

    def test_list_memories(self):
        client.post("/memory", json={"content": "Memory 1"})
        client.post("/memory", json={"content": "Memory 2"})
        resp = client.get("/memory")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_memory(self):
        resp = client.post("/memory", json={"content": "test"})
        mid = resp.json()["id"]
        resp = client.get(f"/memory/{mid}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "test"

    def test_get_memory_not_found(self):
        resp = client.get("/memory/nonexistent")
        assert resp.status_code == 404

    def test_delete_memory(self):
        resp = client.post("/memory", json={"content": "to delete"})
        mid = resp.json()["id"]
        resp = client.delete(f"/memory/{mid}")
        assert resp.status_code == 204
        assert len(store.get_all()) == 0

    def test_delete_memory_not_found(self):
        resp = client.delete("/memory/nonexistent")
        assert resp.status_code == 404

    def test_search(self):
        client.post("/memory", json={"content": "User likes Japanese food"})
        client.post("/memory", json={"content": "User lives in Tokyo"})
        client.post("/memory", json={"content": "User is a Python developer"})
        resp = client.get("/search?q=food&top_k=2&strategy=hybrid")
        assert resp.status_code == 200
        data = resp.json()
        assert data["strategy"] == "hybrid"
        assert len(data["results"]) >= 1

    def test_search_invalid_strategy(self):
        resp = client.get("/search?q=test&strategy=invalid")
        assert resp.status_code == 422

    def test_consolidate(self):
        client.post("/memory", json={"content": "User likes Japanese food"})
        client.post("/memory", json={"content": "User enjoys Japanese meals"})
        resp = client.post("/consolidate", json={"threshold": 0.5})
        assert resp.status_code == 200
        data = resp.json()
        assert "removed" in data
        assert "kept" in data

    def test_build_context(self):
        client.post("/memory", json={"content": "User likes ramen"})
        client.post("/memory", json={"content": "User lives in Tokyo"})
        resp = client.post("/context", json={
            "query": "ramen",
            "template": "default"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "ramen" in data["context"]
        assert data["template"] == "default"

    def test_build_context_compact(self):
        client.post("/memory", json={
            "content": "User likes ramen",
            "metadata": {"category": "preference"}
        })
        resp = client.post("/context", json={
            "query": "ramen",
            "template": "compact",
        })
        assert resp.status_code == 200
        assert "preference" in resp.json()["context"]

    def test_save_and_load(self):
        store.add("test memory", {"category": "test"})
        filepath = "test_memory_data.json"
        resp = client.post(f"/save?filepath={filepath}")
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

        store.clear()
        assert len(store) == 0

        resp = client.post(f"/load?filepath={filepath}")
        assert resp.status_code == 200
        assert store.get_all()[0]["content"] == "test memory"

        import os
        os.remove(filepath)

    def test_search_embedding_engine(self):
        client.post("/memory", json={"content": "User likes Japanese food"})
        client.post("/memory", json={"content": "User lives in Tokyo"})
        resp = client.get("/search?q=food&use_embeddings=true")
        assert resp.status_code == 200
        data = resp.json()
        assert data["engine"] in ("embedding", "tfidf")
        assert len(data["results"]) >= 1

    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_api_version(self):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        assert resp.json()["info"]["version"] == "1.0.0"
