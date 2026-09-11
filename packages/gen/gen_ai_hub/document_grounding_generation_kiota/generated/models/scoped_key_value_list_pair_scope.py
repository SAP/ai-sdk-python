from enum import Enum

class ScopedKeyValueListPair_scope(str, Enum):
    Collection = "collection",
    Document = "document",
    Chunk = "chunk",

