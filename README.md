# agent-memory-runtime

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

agent-memory-runtime 是一个可插拔的 Agent 长期记忆运行时。支持 Python API 和 REST API 两种接入方式，记忆可持久化到 JSON 文件，支持 TF-IDF 和 Embedding 两种语义检索引擎。

---

## 为什么要创建这个项目

LLM Agent 普遍面临四个问题：

1. **跨会话记忆丢失** — 多次独立对话或长时间断开后，模型会遗忘历史状态和用户偏好
2. **上下文窗口有限** — 模型单次能处理的 Token 数量有限，长文本或复杂任务无法一次性输入
3. **检索噪声（记忆污染）** — 长期记忆在提取时混入错误的、过时的或无关的信息，污染当前思考
4. **Token 消耗量大** — 多轮对话、复杂 prompt、ReAct 循环导致 Token 消耗激增

agent-memory-runtime 的思路：**把记忆从 prompt 里抽出来，变成独立的外部系统。** Agent 不直接操作记忆——它调用 memory runtime，由 runtime 决定什么该记、什么该检索、什么该整合。

---

## 架构

```
                         ┌──────────────────┐
                         │   Python / REST   │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┴───────────────────┐
              ▼                                       ▼
┌──────────────────────────┐             ┌──────────────────────────┐
│       写入 (write)        │             │       读取 (read)         │
│                          │             │                          │
│  ┌──────────────────┐    │             │  ┌──────────────────┐    │
│  │  Memory Ingest   │    │             │  │    Retrieval     │    │
│  │  id + 时间戳     │    │             │  │  TF-IDF+Embedding│    │
│  └────────┬─────────┘    │             │  └────────┬─────────┘    │
│           │              │             │           │              │
│           ▼              │             │           ▼              │
│  ┌──────────────────┐    │             │  ┌──────────────────┐    │
│  │  JSON Persist    │    │             │  │     Ranking      │    │
│  │  本地文件存储     │    │             │  │  3 种排序策略     │    │
│  └──────────────────┘    │             │  └────────┬─────────┘    │
│                          │             │           │              │
└──────────────────────────┘             │           ▼              │
                                         │  ┌──────────────────┐    │
                                         │  │  Consolidation   │    │
                                         │  │  合并 + 去重      │    │
                                         │  └────────┬─────────┘    │
                                         │           │              │
                                         │           ▼              │
                                         │  ┌──────────────────┐    │
                                         │  │ Context Builder  │    │
                                         │  │ 记忆 → 自然语言   │    │
                                         │  └────────┬─────────┘    │
                                         │           │              │
                                         └───────────┼──────────────┘
                                                     ▼
                                         ┌──────────────────┐
                                         │      Agent       │
                                         │  prompt + 上下文  │
                                         └──────────────────┘
```

### 层说明

| 层 | 职责 | 状态 |
|----|------|------|
| Memory Ingest | 结构化存储：id + 内容 + metadata + 时间戳 | ✅ |
| Retrieval | 语义搜索：TF-IDF / Embedding 双引擎 | ✅ |
| Ranking | 相关性 + 新鲜度混合排序（3 种策略） | ✅ |
| Consolidation | 相似记忆合并去重 | ✅ |
| Context Builder | 检索结果 → prompt 可用的自然语言 | ✅ |
| JSON Persist | 本地文件持久化，重启不丢失 | ✅ |
| REST API | 9 个端点，FastAPI + Swagger | ✅ |

---

## 📰 News

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

# 持久化存储 — 自动保存到 JSON
store = MemoryStore(filepath="user_memories.json")
store.add("User likes Japanese food, especially ramen and sushi",
          metadata={"category": "preference"})
store.add("User lives in Tokyo, Japan", metadata={"category": "location"})

# TF-IDF 检索
retriever = MemoryRetriever(store)
results = retriever.search("food preference")

# 或 Embedding 检索（需 pip install sentence-transformers）
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
# 启动服务
uvicorn memory.api:app --reload --port 8000

# Swagger 文档 → http://127.0.0.1:8000/docs
```

```bash
# 存入记忆
curl -X POST http://127.0.0.1:8000/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "User likes ramen", "metadata": {"category": "preference"}}'

# TF-IDF 检索
curl "http://127.0.0.1:8000/search?q=ramen&strategy=hybrid&top_k=5"

# Embedding 检索（需安装 sentence-transformers）
curl "http://127.0.0.1:8000/search?q=ramen&use_embeddings=true"

# 持久化到文件
curl -X POST "http://127.0.0.1:8000/save?filepath=my_memories.json"

# 从文件加载
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
