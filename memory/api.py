from fastapi import FastAPI, Query
from pydantic import BaseModel
from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever
from memory.ranking.ranker import MemoryRanker
from memory.consolidation.consolidator import MemoryConsolidator
from memory.context.builder import ContextBuilder


store = MemoryStore()
retriever = MemoryRetriever(store)
ranker = MemoryRanker()
consolidator = MemoryConsolidator()
context_builder = ContextBuilder()

app = FastAPI(title="agent-memory-runtime", version="0.6.0")


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


class SearchResponse(BaseModel):
    query: str
    strategy: str
    results: list[dict]


class ConsolidateResponse(BaseModel):
    removed: int
    merged: int
    kept: int


class ContextResponse(BaseModel):
    template: str
    context: str


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
):
    results = retriever.search(q, top_k=top_k)
    ranked = ranker.rerank(results, strategy=strategy)
    return SearchResponse(query=q, strategy=strategy, results=ranked)


@app.post("/consolidate", response_model=ConsolidateResponse)
def consolidate(body: ConsolidateRequest = ConsolidateRequest()):
    consolidator.threshold = body.threshold
    result = consolidator.consolidate(store)
    return ConsolidateResponse(**result)


@app.post("/context", response_model=ContextResponse)
def build_context(body: ContextRequest):
    results = retriever.search(body.query, top_k=body.top_k)
    ranked = ranker.rerank(results, strategy=body.strategy)
    context_builder.max_tokens = body.max_tokens
    text = context_builder.build(ranked, query=body.query, template=body.template)
    return ContextResponse(template=body.template, context=text)
