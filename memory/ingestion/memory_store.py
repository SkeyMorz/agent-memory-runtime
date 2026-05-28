class MemoryStore:
    def __init__(self):
        self.memories: list[dict] = []

    def add(self, content: str, metadata: dict | None = None) -> str:
        import uuid
        from datetime import datetime, timezone

        memory = {
            "id": uuid.uuid4().hex[:12],
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.memories.append(memory)
        return memory["id"]

    def get_all(self) -> list[dict]:
        return self.memories

    def get(self, memory_id: str) -> dict | None:
        for m in self.memories:
            if m["id"] == memory_id:
                return m
        return None

    def delete(self, memory_id: str) -> bool:
        for i, m in enumerate(self.memories):
            if m["id"] == memory_id:
                self.memories.pop(i)
                return True
        return False

    def clear(self) -> None:
        self.memories.clear()

    def __len__(self) -> int:
        return len(self.memories)
