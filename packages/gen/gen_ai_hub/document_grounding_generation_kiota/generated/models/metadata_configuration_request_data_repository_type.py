from enum import Enum

class MetadataConfigurationRequest_dataRepositoryType(str, Enum):
    MSSharePoint = "MSSharePoint",
    S3 = "S3",
    SFTP = "SFTP",

