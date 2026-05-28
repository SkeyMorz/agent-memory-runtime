from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever
from memory.ranking.ranker import MemoryRanker

store = MemoryStore()

store.add("User likes Japanese food, especially ramen and sushi")
store.add("User is a software engineer working with Python")
store.add("User lives in Tokyo, Japan")
store.add("User enjoys hiking and outdoor activities")

retriever = MemoryRetriever(store)
ranker = MemoryRanker()

results = retriever.search("What food does the user like?", top_k=3)

print("=== semantic (TF-IDF only) ===")
for r in ranker.rerank(results, strategy="semantic"):
    print(f"  [{r['score']:.4f}] {r['content']}")

print("=== recency ===")
for r in ranker.rerank(results, strategy="recency"):
    print(f"  [{r['score']:.4f}] {r['content']}")

print("=== hybrid (default) ===")
for r in ranker.rerank(results, strategy="hybrid"):
    print(f"  [{r['score']:.4f}] {r['content']}")
