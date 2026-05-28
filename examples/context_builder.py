from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever
from memory.ranking.ranker import MemoryRanker
from memory.context.builder import ContextBuilder

store = MemoryStore()

store.add("User likes Japanese food, especially ramen and sushi", metadata={"category": "preference"})
store.add("User lives in Tokyo, Japan", metadata={"category": "location"})
store.add("User is a Python software engineer", metadata={"category": "professional"})
store.add("User enjoys hiking and outdoor activities", metadata={"category": "hobby"})
store.add("User prefers dark mode in all applications", metadata={"category": "preference"})

retriever = MemoryRetriever(store)
ranker = MemoryRanker()
builder = ContextBuilder(max_tokens=500)

results = retriever.search("food preference and location")
ranked = ranker.rerank(results, strategy="hybrid")

print("=== default template ===")
print(builder.build(ranked, query="Recommend a restaurant for the user"))

print("\n=== compact template ===")
print(builder.build(ranked, template="compact"))

print("\n=== system_prompt template ===")
print(builder.build(ranked, template="system_prompt"))
