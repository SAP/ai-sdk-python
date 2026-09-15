from enum import Enum

class ContextSelectionStrategyEnum(str, Enum):
    None_ = "none",
    Random = "random",
    Heuristic = "heuristic",
    Auto = "auto",

