class ContextBuilder:
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens

    def build(self, memories: list[dict], query: str = "", template: str = "default") -> str:
        if template == "compact":
            return self._build_compact(memories)
        if template == "system_prompt":
            return self._build_system_prompt(memories)
        return self._build_default(memories, query)

    def _build_default(self, memories: list[dict], query: str) -> str:
        if not memories:
            return "No relevant memories found."

        lines = ["## Relevant Memories\n"]
        token_budget = self.max_tokens

        for m in memories:
            entry = self._format_entry(m, include_meta=True)
            if self._token_estimate(entry) > token_budget:
                entry = self._format_entry(m, include_meta=False)
            if self._token_estimate(entry) > token_budget:
                break
            lines.append(entry)
            token_budget -= self._token_estimate(entry)

        if query:
            lines.append(f"\nUse the above memories to inform your response to: {query}")

        return "\n".join(lines)

    def _build_compact(self, memories: list[dict]) -> str:
        if not memories:
            return ""

        grouped: dict[str, list[dict]] = {}
        for m in memories:
            cat = m.get("metadata", {}).get("category", "general")
            grouped.setdefault(cat, []).append(m)

        sections = ["## User Context\n"]
        for cat, items in grouped.items():
            facts = "; ".join(
                m["content"].rstrip(".") for m in items[:5]
            )
            sections.append(f"- {cat}: {facts}.")

        return "\n".join(sections)

    def _build_system_prompt(self, memories: list[dict]) -> str:
        if not memories:
            return ""

        lines = [
            "## User Profile (from memory)",
            "The following was learned from previous conversations. "
            "Use it to personalize responses.\n",
        ]
        for m in memories[:10]:
            ts = self._relative_time(m.get("created_at", ""))
            lines.append(f"- [{ts}] {m['content']}")

        return "\n".join(lines)

    def _format_entry(self, m: dict, include_meta: bool = True) -> str:
        score = m.get("score")
        content = m.get("content", "")
        parts = []

        if include_meta:
            cat = m.get("metadata", {}).get("category")
            ts = self._relative_time(m.get("created_at", ""))
            prefix = f"[{ts}]"
            if cat:
                prefix += f" [{cat}]"
            if score is not None:
                prefix += f" ({score:.2f})"
            parts.append(f"- {prefix} {content}")
        else:
            parts.append(f"- {content}")

        return "".join(parts) if parts else f"- {content}"

    def _relative_time(self, iso_string: str) -> str:
        if not iso_string:
            return ""
        try:
            from datetime import datetime, timezone

            dt = datetime.fromisoformat(iso_string)
            now = datetime.now(timezone.utc)
            delta = now - dt

            if delta.days == 0:
                hours = delta.seconds // 3600
                if hours == 0:
                    return "just now"
                return f"{hours}h ago"
            elif delta.days < 7:
                return f"{delta.days}d ago"
            elif delta.days < 30:
                return f"{delta.days // 7}w ago"
            else:
                return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return ""

    def _token_estimate(self, text: str) -> int:
        return len(text.split())
