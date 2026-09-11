from enum import Enum

class ScoresAggregationStrategy(str, Enum):
    Weighted_average = "weighted_average",
    Rrf = "rrf",
    Weighted_rrf = "weighted_rrf",

