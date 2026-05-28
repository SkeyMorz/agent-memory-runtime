from memory.ingestion.memory_store import MemoryStore

memory = MemoryStore()

memory.add("User likes Japanese food")

print(memory.get_all())