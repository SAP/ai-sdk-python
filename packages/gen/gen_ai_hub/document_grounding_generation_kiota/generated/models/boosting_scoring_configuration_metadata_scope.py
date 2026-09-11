from enum import Enum

class BoostingScoringConfiguration_metadata_scope(str, Enum):
    Repository = "repository",
    Document = "document",
    Chunk = "chunk",

