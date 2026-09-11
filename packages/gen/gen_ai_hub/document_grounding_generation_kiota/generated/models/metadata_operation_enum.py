from enum import Enum

class MetadataOperationEnum(str, Enum):
    Add = "add",
    Remove = "remove",
    Replace = "replace",
    Delete_key = "delete_key",

