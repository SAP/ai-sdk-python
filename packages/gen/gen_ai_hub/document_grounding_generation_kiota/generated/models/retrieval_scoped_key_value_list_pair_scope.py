from enum import Enum

class RetrievalScopedKeyValueListPair_scope(str, Enum):
    Repository = "repository",
    Document = "document",
    Chunk = "chunk",

