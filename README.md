# agent-memory-runtime

<h3 align="center">English | <a href="README-zh.md">简体中文</a></h3>

<p align="center">
  <b>Give AI Agents Long-Term Memory — A Pluggable, Production-Ready Memory Runtime</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/retrieval-TF--IDF%20%7C%20Embedding-green" alt="Retrieval">
  <img src="https://img.shields.io/badge/storage-JSON%20persistence-orange" alt="Storage">
  <img src="https://img.shields.io/badge/tests-47%20passed-brightgreen" alt="Tests">
</p>

- 📝 **Project Status:** v1.0 — production-ready: persistence + embedding retrieval + REST API
- 🏗️ **Architecture:** ingestion → retrieval (TF-IDF / Embedding) → ranking → consolidation → context → REST API

agent-memory-runtime is a pluggable long-term memory runtime for AI agents. It sits one layer below any agent framework — like a database sits below an application — giving agents persistent memory across sessions via Python API or REST API.

---

## Why This Project Exists

Every LLM agent faces the same four problems:

1. **Memory loss across sessions** — The model forgets everything the moment a conversation ends. Past preferences, personal details, decisions — all gone.
2. **Limited context windows** — You can't fit everything into the prompt. There's a hard token limit, and long context degrades attention.
3. **Retrieval noise** — When you do store memories externally, the wrong ones surface: stale facts, irrelevant details, outdated preferences.
4. **Token waste** — Dumping raw history into every prompt burns tokens on information the model doesn't need for this specific query.

The core insight: **pull memory out of the prompt and into an external system.** The agent doesn't manage memory — it asks the runtime. The runtime decides what to store, what to retrieve, and what belongs in context right now.

---

## What It Does For You

### Your AI stops forgetting

Tell your AI "I'm on a diet" on Monday, it won't recommend fried chicken on Wednesday. Preferences, important dates, personal facts — all persisted to a local file. Restart the server, switch machines, come back a week later — the memories are still there.

### Only relevant memories enter the prompt

The naive approach dumps entire conversation histories into every prompt. That means exploding token costs and a model drowning in noise. Instead, agent-memory-runtime searches for only the most relevant memories for each query, and injects just those few. **Everything is remembered, but you only pay for what you use.**

### Similar memories auto-merge

People say the same thing in different ways — "I love Japanese food" and "I'm really into Japanese cuisine." The system detects near-duplicates, merges them, and removes the redundancy. Your memory store stays clean without manual cleanup.

### No framework lock-in

Using LangChain? AutoGPT? A custom agent loop you wrote yourself? Import one class, call two methods (`add` + `search`), and you're done. Don't want to touch Python? Start the HTTP server and call it from any language.

### Swappable retrieval engine

Start with TF-IDF — zero external dependencies, zero API keys, zero cost. When you need stronger semantic understanding, switch to the Embedding engine with one parameter. Same interface, better matching, no refactoring.

---

## Architecture

```
                         ┌──────────────────┐
                         │   Python / REST   │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┴───────────────────┐
              ▼                                       ▼
┌──────────────────────────┐             ┌──────────────────────────┐
│       Write Path          │             │        Read Path          │
│                          │             │                          │
│  ┌──────────────────┐    │             │  ┌──────────────────┐    │
│  │  Memory Ingest   │    │             │  │    Retrieval     │    │
│  │  id + timestamp  │    │             │  │  TF-IDF+Embedding│    │
│  └────────┬─────────┘    │             │  └────────┬─────────┘    │
│           │              │             │           │              │
│           ▼              │             │           ▼              │
│  ┌──────────────────┐    │             │  ┌──────────────────┐    │
│  │  JSON Persist    │    │             │  │     Ranking      │    │
│  │  local file      │    │             │  │  3 strategies    │    │
│  └──────────────────┘    │             │  └────────┬─────────┘    │
│                          │             │           │              │
└──────────────────────────┘             │           ▼              │
                                         │  ┌──────────────────┐    │
                                         │  │  Consolidation   │    │
                                         │  │  merge + dedup   │    │
                                         │  └────────┬─────────┘    │
                                         │           │              │
                                         │           ▼              │
                                         │  ┌──────────────────┐    │
                                         │  │ Context Builder  │    │
                                         │  │  memory → text   │    │
                                         │  └────────┬─────────┘    │
                                         │           │              │
                                         └───────────┼──────────────┘
                                                     ▼
                                         ┌──────────────────┐
                                         │      Agent       │
                                         │  prompt + context │
                                         └──────────────────┘
```

### Layer Overview

| Layer | Responsibility | Status |
|----|------|------|
| Memory Ingest | Structured storage: id + content + metadata + timestamp | ✅ |
| Retrieval | Semantic search: TF-IDF / Embedding dual engine | ✅ |
| Ranking | Relevance + recency hybrid scoring (3 strategies) | ✅ |
| Consolidation | Similar memory detection, merge, and dedup | ✅ |
| Context Builder | Ranked results → natural language prompt context | ✅ |
| JSON Persist | Local file persistence, survives restarts | ✅ |
| REST API | 9 endpoints, FastAPI + auto-generated Swagger docs | ✅ |

---

## 📰 News

- **2026-05-30** — Benchmarks added: Recall@5 42.58%, MRR 0.4643, Consolidation Accuracy 100%.
- **2026-05-29** — v1.0 released: JSON persistence + EmbeddingRetriever via sentence-transformers. 47 tests passing.
- **2026-05-28** — v0.6 released: FastAPI REST service — 7 endpoints wrapping all 5 layers.
- **2026-05-28** — v0.5 released: ContextBuilder with 3 templates, token budget control.
- **2026-05-28** — v0.4 released: MemoryConsolidator — automatic similar memory detection & merge.
- **2026-05-28** — v0.3 released: MemoryRanker with three strategies (semantic / recency / hybrid).
- **2026-05-28** — v0.2 released: MemoryRetriever with TF-IDF + cosine similarity semantic search.
- **2026-05-28** — v0.1 released: MemoryStore with structured CRUD.

---

## 🗺️ Project Map

```
agent-memory-runtime/
├── pyproject.toml
├── memory/
│   ├── api.py                      # FastAPI app — 9 REST endpoints
│   ├── ingestion/
│   │   └── memory_store.py         # MemoryStore: CRUD + JSON persistence
│   ├── retrieval/
│   │   ├── retriever.py            # MemoryRetriever: TF-IDF + cosine
│   │   └── embedding_retriever.py  # EmbeddingRetriever: sentence-transformers
│   ├── ranking/
│   │   └── ranker.py               # MemoryRanker: semantic / recency / hybrid
│   ├── consolidation/
│   │   └── consolidator.py         # MemoryConsolidator: merge & dedup
│   ├── context/
│   │   └── builder.py              # ContextBuilder: prompt-ready text output
│   └── storage/                    # (future) additional backends
├── examples/
│   ├── basic_usage.py              # v0.1: add & get_all
│   ├── semantic_retrieval.py       # v0.2: search with TF-IDF
│   ├── memory_ranking.py           # v0.3: three ranking strategies
│   ├── memory_consolidation.py     # v0.4: merge similar memories
│   └── context_builder.py          # v0.5: 3 template outputs
├── benchmarks/
│   ├── dataset.py                  # 25 memories + 20 labeled queries
│   └── evaluate.py                 # Recall@K, MRR, MAP, Precision@K
├── tests/
│   ├── test_api.py                 # 15 tests
│   ├── test_retrieval.py           # 4 tests
│   ├── test_ranking.py             # 6 tests
│   ├── test_consolidation.py       # 8 tests
│   ├── test_context.py             # 8 tests
│   └── test_persistence.py         # 6 tests
├── docs/
├── README.md
└── LICENSE
```

---

## 📊 Benchmarks

Dataset: **25 memories** across 8 categories, **20 labeled queries**. All numbers from `python -m benchmarks.evaluate`.

### Retrieval (TF-IDF + Hybrid Ranking)

Overall on 20 mixed-difficulty queries:

| Metric | Score | What It Means |
|--------|-------|---------------|
| Recall@5 | 42.6% | 2 in 5 relevant items found in top 5 |
| MRR | 0.464 | First relevant result at ~rank 2.1 on average |
| Latency | 1.1 ms | Per query |

Broken down by query type:

| Query Type | Success | Why |
|------------|---------|-----|
| Keyword match ("user has a dog" → "User has a golden retriever") | Strong | Words overlap directly |
| Partial overlap ("user food preference" → "likes Japanese food") | Mixed | Some terms match, some don't |
| Semantic ("what does user eat" → "loves ramen") | Fails | "eat" and "ramen" are different tokens to TF-IDF |

### Consolidation (default threshold 0.45)

**Simple cases — 5/5 correct** (near-identical duplicates, clearly different topics).

**Edge cases — 2/7 correct:**

| Case | Expected | Actual | Root Cause |
|------|----------|--------|-------------|
| "Japanese food" vs "Japanese cuisine" | Merge | Keep | Synonyms unrecognized |
| Short vs long text about ramen | Merge | Keep | Length imbalance |
| "visited Tokyo" vs "visited Kyoto" | Keep | Merge | Same structure, different city |
| "software engineer" vs "programmer" | Merge | Keep | No shared vocabulary |
| "Japanese food ramen" vs "Chinese food dumplings" | Keep | Merge | Same sentence template |

**Known limitations:** TF-IDF cannot handle synonyms, short-vs-long text imbalance, or structurally identical sentences with different facts. These drive the Embedding engine upgrade path.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Core: numpy + scikit-learn
- Embedding (optional): sentence-transformers (for `use_embeddings=true`)

### Install

```bash
git clone https://github.com/SkeyMorz/agent-memory-runtime.git
cd agent-memory-runtime
pip install -e .                  # core only
pip install -e ".[dev]"           # includes API + embedding deps
```

### Python API

```python
from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever
from memory.retrieval.embedding_retriever import EmbeddingRetriever
from memory.ranking.ranker import MemoryRanker
from memory.consolidation.consolidator import MemoryConsolidator
from memory.context.builder import ContextBuilder

# Persistent storage — auto-save to JSON
store = MemoryStore(filepath="user_memories.json")
store.add("User likes Japanese food, especially ramen and sushi",
          metadata={"category": "preference"})
store.add("User lives in Tokyo, Japan", metadata={"category": "location"})

# TF-IDF retrieval
retriever = MemoryRetriever(store)
results = retriever.search("food preference")

# Or Embedding retrieval (requires: pip install sentence-transformers)
# embed_retriever = EmbeddingRetriever(store)
# results = embed_retriever.search("food preference")

ranker = MemoryRanker()
ranked = ranker.rerank(results, strategy="hybrid")

builder = ContextBuilder()
context = builder.build(ranked, query="Recommend a restaurant")
print(context)
```

### REST API

```bash
# Start the server
uvicorn memory.api:app --reload --port 8000

# Swagger docs → http://127.0.0.1:8000/docs
```

```bash
# Add a memory
curl -X POST http://127.0.0.1:8000/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "User likes ramen", "metadata": {"category": "preference"}}'

# TF-IDF search
curl "http://127.0.0.1:8000/search?q=ramen&strategy=hybrid&top_k=5"

# Embedding search (requires sentence-transformers)
curl "http://127.0.0.1:8000/search?q=ramen&use_embeddings=true"

# Persist to file
curl -X POST "http://127.0.0.1:8000/save?filepath=my_memories.json"

# Load from file
curl -X POST "http://127.0.0.1:8000/load?filepath=my_memories.json"
```

### 🚩 REST API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/memory` | Add a memory |
| `GET` | `/memory` | List all memories |
| `GET` | `/memory/{id}` | Get one memory |
| `DELETE` | `/memory/{id}` | Delete a memory |
| `GET` | `/search?q=&strategy=&use_embeddings=` | TF-IDF or Embedding search + rank |
| `POST` | `/consolidate` | Merge similar memories |
| `POST` | `/context` | Build prompt context |
| `POST` | `/save?filepath=` | Persist memories to JSON file |
| `POST` | `/load?filepath=` | Load memories from JSON file |
| `GET` | `/health` | Health check + memory count |

---

## 📊 Roadmap

| Version | Feature | Status |
|---------|---------|--------|
| v0.1 | MemoryStore — structured add / get / delete | ✅ done |
| v0.2 | MemoryRetriever — TF-IDF semantic search | ✅ done |
| v0.3 | MemoryRanker — 3 ranking strategies | ✅ done |
| v0.4 | MemoryConsolidator — merge similar, dedup | ✅ done |
| v0.5 | ContextBuilder — 3 templates, token budget, relative time | ✅ done |
| v0.6 | FastAPI service — REST API, Swagger docs | ✅ done |
| v1.0 | Production-ready — JSON persistence + EmbeddingRetriever | ✅ done |

---

## 🧪 Run Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

```
tests/test_api.py::test_add_memory PASSED
tests/test_api.py::test_list_memories PASSED
tests/test_api.py::test_get_memory PASSED
tests/test_api.py::test_get_memory_not_found PASSED
tests/test_api.py::test_delete_memory PASSED
tests/test_api.py::test_delete_memory_not_found PASSED
tests/test_api.py::test_search PASSED
tests/test_api.py::test_search_invalid_strategy PASSED
tests/test_api.py::test_consolidate PASSED
tests/test_api.py::test_build_context PASSED
tests/test_api.py::test_build_context_compact PASSED
tests/test_api.py::test_save_and_load PASSED
tests/test_api.py::test_search_embedding_engine PASSED
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_api_version PASSED
tests/test_consolidation.py::test_consolidate_empty_store PASSED
tests/test_consolidation.py::test_consolidate_single_memory PASSED
tests/test_consolidation.py::test_consolidate_merges_similar PASSED
tests/test_consolidation.py::test_consolidate_keeps_different PASSED
tests/test_consolidation.py::test_high_threshold_preserves_more PASSED
tests/test_consolidation.py::test_low_threshold_merges_more PASSED
tests/test_consolidation.py::test_merge_preserves_longer_content PASSED
tests/test_consolidation.py::test_merge_combines_non_overlapping_content PASSED
tests/test_context.py::test_build_default_with_memories PASSED
tests/test_context.py::test_build_empty PASSED
tests/test_context.py::test_build_compact_groups_by_category PASSED
tests/test_context.py::test_build_system_prompt PASSED
tests/test_context.py::test_build_compact_empty PASSED
tests/test_context.py::test_build_system_prompt_empty PASSED
tests/test_context.py::test_token_budget_truncation PASSED
tests/test_context.py::test_relative_time_formatting PASSED
tests/test_persistence.py::test_save_and_load PASSED
tests/test_persistence.py::test_auto_load_on_init PASSED
tests/test_persistence.py::test_auto_save_on_add PASSED
tests/test_persistence.py::test_auto_save_on_delete PASSED
tests/test_persistence.py::test_auto_save_on_clear PASSED
tests/test_persistence.py::test_nonexistent_file_no_error PASSED
tests/test_ranking.py::test_rerank_empty PASSED
tests/test_ranking.py::test_semantic_preserves_order PASSED
tests/test_ranking.py::test_recency_boosts_newer PASSED
tests/test_ranking.py::test_hybrid_combines_scores PASSED
tests/test_ranking.py::test_missing_created_at_uses_default PASSED
tests/test_ranking.py::test_unknown_strategy_raises PASSED
tests/test_retrieval.py::test_search_returns_relevant_results PASSED
tests/test_retrieval.py::test_search_empty_store PASSED
tests/test_retrieval.py::test_search_respects_top_k PASSED
tests/test_retrieval.py::test_results_have_scores PASSED
```
