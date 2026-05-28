class MemoryStore:
    def __init__(self):
        self.memories = []

    def add(self, content):
        self.memories.append(content)

    def get_all(self):
        return self.memories