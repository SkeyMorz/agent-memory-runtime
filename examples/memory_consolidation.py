from memory.ingestion.memory_store import MemoryStore
from memory.consolidation.consolidator import MemoryConsolidator

store = MemoryStore()

store.add("User likes Japanese food, especially ramen and sushi")
store.add("User loves Japanese cuisine like ramen and sushi")
store.add("User is a Python software engineer")
store.add("User enjoys hiking and outdoor activities")
store.add("User likes going on hikes and spending time outdoors")

print(f"Before consolidation: {len(store)} memories")
for m in store.get_all():
    print(f"  [{m['id']}] {m['content']}")

consolidator = MemoryConsolidator(threshold=0.45)
result = consolidator.consolidate(store)

print(f"\nResult: {result}")
print(f"After consolidation: {len(store)} memories")
for m in store.get_all():
    print(f"  [{m['id']}] {m['content']}")
