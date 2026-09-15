from enum import Enum

class TaskTypeEnum(str, Enum):
    Classification = "classification",
    Regression = "regression",

