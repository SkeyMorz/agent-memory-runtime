import pytest
from datetime import datetime, timezone, timedelta
from memory.context.builder import ContextBuilder


class TestContextBuilder:
    def test_build_default_with_memories(self):
        builder = ContextBuilder()
        memories = [
            {"id": "1", "content": "User likes ramen", "score": 0.9,
             "metadata": {"category": "preference"},
             "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": "2", "content": "User lives in Tokyo", "score": 0.7,
             "metadata": {"category": "location"},
             "created_at": datetime.now(timezone.utc).isoformat()},
        ]
        result = builder.build(memories, query="Where to eat?")
        assert "User likes ramen" in result
        assert "User lives in Tokyo" in result
        assert "Where to eat?" in result

    def test_build_empty(self):
        builder = ContextBuilder()
        result = builder.build([], template="default")
        assert "No relevant memories" in result

    def test_build_compact_groups_by_category(self):
        builder = ContextBuilder()
        memories = [
            {"id": "1", "content": "Likes dark mode", "metadata": {"category": "preference"},
             "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": "2", "content": "Is a Python dev", "metadata": {"category": "professional"},
             "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": "3", "content": "Uses VS Code", "metadata": {"category": "professional"},
             "created_at": datetime.now(timezone.utc).isoformat()},
        ]
        result = builder.build(memories, template="compact")
        assert "preference" in result
        assert "professional" in result
        assert "Likes dark mode" in result
        assert "Is a Python dev" in result

    def test_build_system_prompt(self):
        builder = ContextBuilder()
        memories = [
            {"id": "1", "content": "User prefers tea over coffee",
             "created_at": datetime.now(timezone.utc).isoformat()},
        ]
        result = builder.build(memories, template="system_prompt")
        assert "User Profile" in result
        assert "prefers tea over coffee" in result

    def test_build_compact_empty(self):
        builder = ContextBuilder()
        result = builder.build([], template="compact")
        assert result == ""

    def test_build_system_prompt_empty(self):
        builder = ContextBuilder()
        result = builder.build([], template="system_prompt")
        assert result == ""

    def test_token_budget_truncation(self):
        builder = ContextBuilder(max_tokens=10)
        memories = [
            {"id": "1", "content": "A" * 500, "score": 0.9,
             "metadata": {}, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": "2", "content": "B" * 500, "score": 0.8,
             "metadata": {}, "created_at": datetime.now(timezone.utc).isoformat()},
        ]
        result = builder.build(memories, template="default")
        assert result.count("- [") <= 2

    def test_relative_time_formatting(self):
        builder = ContextBuilder()
        now = datetime.now(timezone.utc)
        memories = [
            {"id": "1", "content": "test",
             "created_at": (now - timedelta(days=3)).isoformat()},
        ]
        result = builder.build(memories, template="system_prompt")
        assert "3d ago" in result
