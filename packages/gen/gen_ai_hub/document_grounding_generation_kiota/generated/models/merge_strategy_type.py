from enum import Enum

class MergeStrategyType(str, Enum):
    Reranker = "reranker",
    ScoreReuse = "scoreReuse",
    ReciprocalRankFusion = "reciprocalRankFusion",
    Random = "random",

