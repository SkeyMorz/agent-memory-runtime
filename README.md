# agent-memory-runtime

<p align="center">
  <b>Give AI Agents Long-Term Memory — A Pluggable Memory Runtime</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/retrieval-TF--IDF%20%2B%20cosine-green" alt="Retrieval">
  <img src="https://img.shields.io/badge/layers-Ingestion%20%7C%20Retrieval%20%7C%20Ranking%20%7C%20Consolidation-orange" alt="Layers">
  <img src="https://img.shields.io/badge/tests-18%20passed-brightgreen" alt="Tests">
</p>

- 📝 **Project Status:** v0.4 — ingestion → retrieval → ranking → consolidation done, context builder next
- 🏗️ **Architecture:** 5-layer memory pipeline (ingestion → retrieval → ranking → consolidation → context)

agent-memory-runtime 是一个可插拔的 Agent 长期记忆运行时。它不绑定任何 Agent 框架——就像数据库之于后端服务，任何 LLM Agent 都可以接入，获得跨会话的持久记忆能力。

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
                ┌────────────────┐
                │     Agent      │
                └───────┬────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ Context Builder  │
              └────────┬─────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌──────────────┐             ┌────────────────┐
│ Short Memory │             │ Long-term Store│
└──────────────┘             └────────────────┘
                                      │
                                      ▼
                           ┌──────────────────┐
                           │ Vector Retrieval │
                           └──────────────────┘
```

### 5 层管道

| 层 | 做什么 | 代码位置 | 状态 |
|----|--------|----------|------|
| Ingestion | 结构化存储每条记忆（id + 时间戳 + metadata） | `memory/ingestion/` | ✅ done |
| Retrieval | 语义搜索（TF-IDF + cosine similarity） | `memory/retrieval/` | ✅ done |
| Ranking | 相关性 + 新鲜度混合排序（3 种策略） | `memory/ranking/` | ✅ done |
| Consolidation | 合并相似记忆，去重去噪 | `memory/consolidation/` | ✅ done |
| Context Builder | 把检索结果拼成 prompt 可用的上下文 | `memory/context/` | 📋 planned |

---

## 📰 News

- **2026-05-28** — v0.4 released: MemoryConsolidator — automatic similar memory detection & merge, 18 tests passing.
- **2026-05-28** — v0.3 released: MemoryRanker with three strategies (semantic / recency / hybrid).
- **2026-05-28** — v0.2 released: MemoryRetriever with TF-IDF + cosine similarity semantic search.
- **2026-05-28** — v0.1 released: MemoryStore with structured CRUD, id + metadata + timestamp per memory.

---

## 🗺️ Project Map

```
agent-memory-runtime/
├── pyproject.toml
├── memory/
│   ├── ingestion/
│   │   └── memory_store.py         # MemoryStore: add / get / delete / clear
│   ├── retrieval/
│   │   └── retriever.py            # MemoryRetriever: TF-IDF + cosine search
│   ├── ranking/
│   │   └── ranker.py               # MemoryRanker: semantic / recency / hybrid
│   ├── consolidation/
│   │   └── consolidator.py         # MemoryConsolidator: merge & dedup
│   ├── context/                    # (planned v0.5) build prompt context
│   └── storage/                    # (planned) persistent backends
├── examples/
│   ├── basic_usage.py              # v0.1: add & get_all
│   ├── semantic_retrieval.py       # v0.2: search with TF-IDF
│   ├── memory_ranking.py           # v0.3: three ranking strategies
│   └── memory_consolidation.py     # v0.4: merge similar memories
├── tests/
│   ├── test_retrieval.py           # 4 tests
│   ├── test_ranking.py             # 6 tests
│   └── test_consolidation.py       # 8 tests
├── docs/
├── README.md
└── LICENSE
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- numpy + scikit-learn (auto-installed with `pip install -e .`)

### Install

```bash
git clone https://github.com/SkeyMorz/agent-memory-runtime.git
cd agent-memory-runtime
pip install -e .
```

### Run — 完整 4 层管道

```python
from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever
from memory.ranking.ranker import MemoryRanker
from memory.consolidation.consolidator import MemoryConsolidator

store = MemoryStore()

# 第 1 次会话：存入记忆
store.add("User likes Japanese food, especially ramen and sushi")
store.add("User loves Japanese cuisine like ramen and sushi")   # 相似记忆
store.add("User lives in Tokyo, Japan")
store.add("User is a Python software engineer")

# 清理重复记忆
consolidator = MemoryConsolidator()
result = consolidator.consolidate(store)
print(f"Merged {result['merged']}, removed {result['removed']}, kept {result['kept']}")

# 第 N 次会话：检索 + 排序
retriever = MemoryRetriever(store)
ranker = MemoryRanker()

results = retriever.search("What food does the user like?")
ranked = ranker.rerank(results, strategy="hybrid")

for m in ranked:
    print(f"[{m['score']:.4f}] {m['content']}")
```

### 🚩 Ranking Strategies

| Strategy | Behavior | Use When |
|----------|----------|----------|
| `semantic` | Pure TF-IDF relevance order | Exact keyword queries |
| `recency` | Exponential decay by age (halflife: 7 days) | Prefer fresh information |
| `hybrid` | 0.7 × semantic + 0.3 × recency (default) | Balance relevance and freshness |

---

## 📊 Roadmap

| Version | Feature | Status |
|---------|---------|--------|
| v0.1 | MemoryStore — structured add / get / delete | ✅ done |
| v0.2 | MemoryRetriever — TF-IDF semantic search | ✅ done |
| v0.3 | MemoryRanker — 3 ranking strategies | ✅ done |
| v0.4 | MemoryConsolidator — merge similar, dedup | ✅ done |
| v0.5 | Context builder — assemble prompt context | 🔜 next |
| v0.6 | FastAPI service — REST API for memory runtime | 📋 planned |
| v1.0 | Production-ready runtime — persistent storage, embeddings | 📋 planned |

---

## 🧪 Run Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

```
tests/test_consolidation.py::test_consolidate_empty_store PASSED
tests/test_consolidation.py::test_consolidate_single_memory PASSED
tests/test_consolidation.py::test_consolidate_merges_similar PASSED
tests/test_consolidation.py::test_consolidate_keeps_different PASSED
tests/test_consolidation.py::test_high_threshold_preserves_more PASSED
tests/test_consolidation.py::test_low_threshold_merges_more PASSED
tests/test_consolidation.py::test_merge_preserves_longer_content PASSED
tests/test_consolidation.py::test_merge_combines_non_overlapping_content PASSED
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
