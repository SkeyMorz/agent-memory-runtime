from memory.ingestion.memory_store import MemoryStore
from memory.retrieval.retriever import MemoryRetriever

store = MemoryStore()

store.add("User likes Japanese food, especially ramen and sushi")
store.add("User is a software engineer working with Python")
store.add("User lives in Tokyo, Japan")
store.add("User enjoys hiking and outdoor activities")

retriever = MemoryRetriever(store)

results = retriever.search("What food does the user like?", top_k=2)
for r in results:
    print(f"[{r['score']:.2f}] {r['content']}")

print("---")

results = retriever.search("Where does the user live?", top_k=2)
for r in results:
    print(f"[{r['score']:.2f}] {r['content']}")
