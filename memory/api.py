import os
from fastapi import FastAPI, Query
from pydantic import BaseModel
from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever
from memory.retrieval.embedding_retriever import EmbeddingRetriever
from memory.ranking.ranker import MemoryRanker
from memory.consolidation.consolidator import MemoryConsolidator
from memory.context.builder import ContextBuilder


DATA_FILE = os.environ.get("MEMORY_DATA_FILE", "memory_data.json")

store = MemoryStore(filepath=DATA_FILE)
retriever = MemoryRetriever(store)
embedding_retriever = EmbeddingRetriever(store)
ranker = MemoryRanker()
consolidator = MemoryConsolidator()
context_builder = ContextBuilder()

app = FastAPI(title="agent-memory-runtime", version="1.0.0")


class MemoryAdd(BaseModel):
    content: str
    metadata: dict | None = None


class MemoryResponse(BaseModel):
    id: str
    content: str
    metadata: dict
    created_at: str


class ConsolidateRequest(BaseModel):
    threshold: float = 0.45


class ContextRequest(BaseModel):
    query: str = ""
    template: str = "default"
    max_tokens: int = 2000
    strategy: str = "hybrid"
    top_k: int = 10
    use_embeddings: bool = False


class SearchResponse(BaseModel):
    query: str
    strategy: str
    engine: str
    results: list[dict]


class ConsolidateResponse(BaseModel):
    removed: int
    merged: int
    kept: int


class ContextResponse(BaseModel):
    template: str
    context: str


class PersistResponse(BaseModel):
    filepath: str
    count: int


def _select_retriever(use_embeddings: bool):
    if use_embeddings:
        try:
            _ = embedding_retriever.model
            return embedding_retriever, "embedding"
        except Exception:
            pass
    return retriever, "tfidf"


@app.post("/memory", response_model=MemoryResponse, status_code=201)
def add_memory(body: MemoryAdd):
    mid = store.add(body.content, body.metadata)
    m = store.get(mid)
    return MemoryResponse(**m)


@app.get("/memory", response_model=list[MemoryResponse])
def list_memories():
    return [MemoryResponse(**m) for m in store.get_all()]


@app.get("/memory/{memory_id}", response_model=MemoryResponse)
def get_memory(memory_id: str):
    m = store.get(memory_id)
    if m is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryResponse(**m)


@app.delete("/memory/{memory_id}", status_code=204)
def delete_memory(memory_id: str):
    if not store.delete(memory_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Memory not found")


@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=50),
    strategy: str = Query("hybrid", pattern="^(semantic|recency|hybrid)$"),
    use_embeddings: bool = Query(False, description="Use embedding-based retrieval"),
):
    r, engine = _select_retriever(use_embeddings)
    results = r.search(q, top_k=top_k)
    ranked = ranker.rerank(results, strategy=strategy)
    return SearchResponse(query=q, strategy=strategy, engine=engine, results=ranked)


@app.post("/consolidate", response_model=ConsolidateResponse)
def consolidate(body: ConsolidateRequest = ConsolidateRequest()):
    consolidator.threshold = body.threshold
    result = consolidator.consolidate(store)
    return ConsolidateResponse(**result)


@app.post("/context", response_model=ContextResponse)
def build_context(body: ContextRequest):
    r, _engine = _select_retriever(body.use_embeddings)
    results = r.search(body.query, top_k=body.top_k)
    ranked = ranker.rerank(results, strategy=body.strategy)
    context_builder.max_tokens = body.max_tokens
    text = context_builder.build(ranked, query=body.query, template=body.template)
    return ContextResponse(template=body.template, context=text)


@app.post("/save", response_model=PersistResponse)
def save(filepath: str = Query(DATA_FILE)):
    store.save(filepath)
    return PersistResponse(filepath=filepath, count=len(store))


@app.post("/load", response_model=PersistResponse)
def load(filepath: str = Query(DATA_FILE)):
    store.load(filepath)
    return PersistResponse(filepath=filepath, count=len(store))


@app.get("/health")
def health():
    return {"status": "ok", "memory_count": len(store)}
