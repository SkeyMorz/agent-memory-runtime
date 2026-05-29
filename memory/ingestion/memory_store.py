import json
import os
import uuid
from datetime import datetime, timezone


class MemoryStore:
    def __init__(self, filepath: str | None = None):
        self.memories: list[dict] = []
        self._filepath = filepath
        if filepath and os.path.exists(filepath):
            self.load(filepath)

    def add(self, content: str, metadata: dict | None = None) -> str:
        memory = {
            "id": uuid.uuid4().hex[:12],
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.memories.append(memory)
        self._auto_save()
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
                self._auto_save()
                return True
        return False

    def clear(self) -> None:
        self.memories.clear()
        self._auto_save()

    def save(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            self.memories = json.load(f)

    def _auto_save(self) -> None:
        if self._filepath:
            self.save(self._filepath)

    def __len__(self) -> int:
        return len(self.memories)
