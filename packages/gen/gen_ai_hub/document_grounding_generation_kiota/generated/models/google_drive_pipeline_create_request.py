from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .google_drive_configuration_struct import GoogleDriveConfigurationStruct
    from .google_drive_pipeline_create_request_type import GoogleDrivePipelineCreateRequest_type
    from .meta_data import MetaData

@dataclass
class GoogleDrivePipelineCreateRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The configuration property
    configuration: Optional[GoogleDriveConfigurationStruct] = None
    # The metadata property
    metadata: Optional[MetaData] = None
    # The type property
    type: Optional[GoogleDrivePipelineCreateRequest_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GoogleDrivePipelineCreateRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GoogleDrivePipelineCreateRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GoogleDrivePipelineCreateRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .google_drive_configuration_struct import GoogleDriveConfigurationStruct
        from .google_drive_pipeline_create_request_type import GoogleDrivePipelineCreateRequest_type
        from .meta_data import MetaData

        from .google_drive_configuration_struct import GoogleDriveConfigurationStruct
        from .google_drive_pipeline_create_request_type import GoogleDrivePipelineCreateRequest_type
        from .meta_data import MetaData

        fields: dict[str, Callable[[Any], None]] = {
            "configuration": lambda n : setattr(self, 'configuration', n.get_object_value(GoogleDriveConfigurationStruct)),
            "metadata": lambda n : setattr(self, 'metadata', n.get_object_value(MetaData)),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(GoogleDrivePipelineCreateRequest_type)),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_object_value("configuration", self.configuration)
        writer.write_object_value("metadata", self.metadata)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

