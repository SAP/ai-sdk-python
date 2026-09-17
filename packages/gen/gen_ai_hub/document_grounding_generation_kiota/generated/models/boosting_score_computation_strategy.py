from enum import Enum

class BoostingScoreComputationStrategy(str, Enum):
    Match_count = "match_count",
    Embedding = "embedding",

