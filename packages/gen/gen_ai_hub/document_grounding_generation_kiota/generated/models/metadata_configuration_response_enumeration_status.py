from enum import Enum

class MetadataConfigurationResponse_enumerationStatus(str, Enum):
    NEW = "NEW",
    IN_PROGRESS = "IN_PROGRESS",
    COMPLETED = "COMPLETED",
    ERROR = "ERROR",

