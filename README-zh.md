# agent-memory-runtime

<h3 align="center"><a href="README.md">English</a> | 简体中文</h3>

<p align="center">
  <b>给 AI Agent 装上长期记忆——一个可插拔、可投产的记忆运行时</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/retrieval-TF--IDF%20%7C%20Embedding-green" alt="Retrieval">
  <img src="https://img.shields.io/badge/storage-JSON%20persistence-orange" alt="Storage">
  <img src="https://img.shields.io/badge/tests-47%20passed-brightgreen" alt="Tests">
</p>

- 📝 **项目状态:** v1.0 — 可投产：持久化存储 + Embedding 检索 + REST API
- 🏗️ **架构:** ingestion → retrieval (TF-IDF / Embedding) → ranking → consolidation → context → REST API

agent-memory-runtime 是一个可插拔的 Agent 长期记忆运行时。它不绑定任何 Agent 框架——就像数据库之于后端服务，任何 LLM Agent 都可以通过 Python API 或 REST API 接入，获得跨会话的持久记忆能力。

---

## 为什么要创建这个项目

LLM Agent 普遍面临四个问题：

1. **跨会话记忆丢失** — 多次独立对话或长时间断开后，模型会遗忘历史状态和用户偏好
2. **上下文窗口有限** — 模型单次能处理的 Token 数量有限，长文本或复杂任务无法一次性输入
3. **检索噪声（记忆污染）** — 长期记忆在提取时混入错误的、过时的或无关的信息，污染当前思考
4. **Token 消耗量大** — 多轮对话、复杂 prompt、ReAct 循环导致 Token 消耗激增

核心思路：**把记忆从 prompt 里抽出来，变成独立的外部系统。** Agent 不直接操作记忆——它调用 memory runtime，由 runtime 决定什么该记、什么该检索、什么该整合。

---

## 它可以为你带来什么

### AI 不会再失忆

周一告诉 AI"我在减肥"，周三它不会推荐炸鸡。用户偏好、重要日期、个人事实——全部持久化到本地文件。重启服务、换机器、过了一周再回来——记忆还在。

### 只筛选相关记忆塞入 prompt

传统做法是把历史对话全塞进 prompt，结果就是 Token 费用爆炸、模型注意力涣散。agent-memory-runtime 的做法是：先语义搜索最相关的几条记忆，只把这部分拼进去。**全部记着，但只为真正用到的那部分付费。**

### 自检相似记忆，合并去重

人会在不同时间说相似的话——"我喜欢日本料理"和"我特别爱吃日料"。系统自动检测近似重复、合并内容、删除冗余。记忆库不会无限膨胀，也不需要手动清理。

### 无需更换框架

用 LangChain？AutoGPT？自己写的 Agent 循环？import 一个 class，调两个方法（`add` + `search`），就接上了。不想写 Python？起一个 HTTP 服务，任何语言都能调。

### 检索引擎可替换

当前用 TF-IDF 起步——零外部依赖、零 API 密钥、零成本。需要更强的语义理解时，一个参数切换到 Embedding 引擎。接口不变，能力升级，不需要重构。

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
│       写入 (Write)        │             │       读取 (Read)         │
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
| Consolidation | 相似记忆检测、合并、去重 | ✅ |
| Context Builder | 排序结果 → prompt 可用的自然语言 | ✅ |
| JSON Persist | 本地文件持久化，重启不丢失 | ✅ |
| REST API | 9 个端点，FastAPI + Swagger 自动文档 | ✅ |

---

## 📰 News

- **2026-05-30** — 评测体系上线：Recall@5 42.58%，MRR 0.4643，记忆合并准确率 100%。
- **2026-05-29** — v1.0 发布：JSON 持久化 + EmbeddingRetriever（sentence-transformers），47 个测试全部通过。
- **2026-05-28** — v0.6 发布：FastAPI REST 服务——7 个端点覆盖全部 5 层。
- **2026-05-28** — v0.5 发布：ContextBuilder，3 种模板，Token 预算控制。
- **2026-05-28** — v0.4 发布：MemoryConsolidator——自动检测并合并相似记忆。
- **2026-05-28** — v0.3 发布：MemoryRanker，3 种排序策略（semantic / recency / hybrid）。
- **2026-05-28** — v0.2 发布：MemoryRetriever，TF-IDF + cosine similarity 语义搜索。
- **2026-05-28** — v0.1 发布：MemoryStore，结构化 CRUD。

---

## 🗺️ 项目结构

```
agent-memory-runtime/
├── pyproject.toml
├── memory/
│   ├── api.py                      # FastAPI 应用 — 9 个 REST 端点
│   ├── ingestion/
│   │   └── memory_store.py         # MemoryStore: CRUD + JSON 持久化
│   ├── retrieval/
│   │   ├── retriever.py            # MemoryRetriever: TF-IDF + cosine
│   │   └── embedding_retriever.py  # EmbeddingRetriever: sentence-transformers
│   ├── ranking/
│   │   └── ranker.py               # MemoryRanker: semantic / recency / hybrid
│   ├── consolidation/
│   │   └── consolidator.py         # MemoryConsolidator: 合并 + 去重
│   ├── context/
│   │   └── builder.py              # ContextBuilder: prompt 文本输出
│   └── storage/                    # （未来）更多存储后端
├── examples/
│   ├── basic_usage.py              # v0.1: add & get_all
│   ├── semantic_retrieval.py       # v0.2: TF-IDF 搜索
│   ├── memory_ranking.py           # v0.3: 3 种排序策略
│   ├── memory_consolidation.py     # v0.4: 合并相似记忆
│   └── context_builder.py          # v0.5: 3 种模板输出
├── tests/
│   ├── test_api.py                 # 15 个测试
│   ├── test_retrieval.py           # 4 个测试
│   ├── test_ranking.py             # 6 个测试
│   ├── test_consolidation.py       # 8 个测试
│   ├── test_context.py             # 8 个测试
│   └── test_persistence.py         # 6 个测试
├── docs/
├── README.md
├── README-zh.md
└── LICENSE
```

---

## 📊 性能评测

数据集：**25 条记忆**，8 个类别，**20 组标注查询**。所有数据来自 `python -m benchmarks.evaluate`。

### 检索性能（TF-IDF + Hybrid Ranking）

整体指标：

| 指标 | 分数 | 含义 |
|--------|-------|------|
| Recall@5 | 42.6% | 前 5 条结果中找到 2/5 相关记忆 |
| MRR | 0.464 | 首个相关结果平均排在第 2.1 位 |
| 延迟 | 1.1 ms | 单次查询 |

按查询类型分解：

| 查询类型 | 效果 | 原因 |
|------------|------|------|
| 关键词匹配 | 强 | 词汇直接重叠 |
| 部分重叠 | 中等 | 部分词匹配 |
| 语义查询 | 失败 | "eat" 和 "ramen" 是不同的词 |

### 记忆合并（默认阈值 0.45）

简单场景 5/5 正确。边缘场景 2/7 正确：

| 场景 | 期望 | 实际 | 根因 |
|------|----------|--------|------|
| 同义词（"food" vs "cuisine"） | 合并 | 保留 | 同义词未识别 |
| 短文本 vs 长文本 | 合并 | 保留 | 长度失衡 |
| 句式相同事实不同 | 保留 | 合并 | 结构相似性误导 |
| 同义职业（"engineer" vs "programmer"） | 合并 | 保留 | 无共有词汇 |

**已知局限：** TF-IDF 无法处理同义词和语义关系。这些正是 Embedding 引擎设计的出发点。

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 核心依赖：numpy + scikit-learn
- Embedding（可选）：sentence-transformers（启用 `use_embeddings=true` 时需要）

### 安装

```bash
git clone https://github.com/SkeyMorz/agent-memory-runtime.git
cd agent-memory-runtime
pip install -e .                  # 仅核心
pip install -e ".[dev]"           # 含 API + Embedding 依赖
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
store.add("用户喜欢日本料理，尤其是拉面和寿司",
          metadata={"category": "preference"})
store.add("用户住在东京", metadata={"category": "location"})

# TF-IDF 检索
retriever = MemoryRetriever(store)
results = retriever.search("food preference")

# 或 Embedding 检索（需先 pip install sentence-transformers）
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
# 添加记忆
curl -X POST http://127.0.0.1:8000/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "User likes ramen", "metadata": {"category": "preference"}}'

# TF-IDF 搜索
curl "http://127.0.0.1:8000/search?q=ramen&strategy=hybrid&top_k=5"

# Embedding 搜索（需安装 sentence-transformers）
curl "http://127.0.0.1:8000/search?q=ramen&use_embeddings=true"

# 持久化到文件
curl -X POST "http://127.0.0.1:8000/save?filepath=my_memories.json"

# 从文件加载
curl -X POST "http://127.0.0.1:8000/load?filepath=my_memories.json"
```

### 🚩 REST API 端点

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/memory` | 添加记忆 |
| `GET` | `/memory` | 列出全部记忆 |
| `GET` | `/memory/{id}` | 获取单条记忆 |
| `DELETE` | `/memory/{id}` | 删除记忆 |
| `GET` | `/search?q=&strategy=&use_embeddings=` | TF-IDF 或 Embedding 搜索 + 排序 |
| `POST` | `/consolidate` | 合并相似记忆 |
| `POST` | `/context` | 生成 prompt 上下文 |
| `POST` | `/save?filepath=` | 持久化记忆到 JSON 文件 |
| `POST` | `/load?filepath=` | 从 JSON 文件加载记忆 |
| `GET` | `/health` | 健康检查 + 记忆数量 |

---

## 📊 Roadmap

| 版本 | 功能 | 状态 |
|---------|---------|--------|
| v0.1 | MemoryStore — 结构化 add / get / delete | ✅ done |
| v0.2 | MemoryRetriever — TF-IDF 语义搜索 | ✅ done |
| v0.3 | MemoryRanker — 3 种排序策略 | ✅ done |
| v0.4 | MemoryConsolidator — 合并相似、去重 | ✅ done |
| v0.5 | ContextBuilder — 3 种模板、Token 预算、相对时间 | ✅ done |
| v0.6 | FastAPI 服务 — REST API、Swagger 文档 | ✅ done |
| v1.0 | 可投产 — JSON 持久化 + EmbeddingRetriever | ✅ done |

---

## 🧪 运行测试

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
