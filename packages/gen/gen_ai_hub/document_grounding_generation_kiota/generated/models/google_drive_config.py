from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .google_drive_config_resource_type import GoogleDriveConfig_resourceType

@dataclass
class GoogleDriveConfig(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The includePaths property
    include_paths: Optional[list[str]] = None
    # The resourceId property
    resource_id: Optional[str] = None
    # The resourceType property
    resource_type: Optional[GoogleDriveConfig_resourceType] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GoogleDriveConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GoogleDriveConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GoogleDriveConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .google_drive_config_resource_type import GoogleDriveConfig_resourceType

        from .google_drive_config_resource_type import GoogleDriveConfig_resourceType

        fields: dict[str, Callable[[Any], None]] = {
            "includePaths": lambda n : setattr(self, 'include_paths', n.get_collection_of_primitive_values(str)),
            "resourceId": lambda n : setattr(self, 'resource_id', n.get_str_value()),
            "resourceType": lambda n : setattr(self, 'resource_type', n.get_enum_value(GoogleDriveConfig_resourceType)),
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
        writer.write_collection_of_primitive_values("includePaths", self.include_paths)
        writer.write_str_value("resourceId", self.resource_id)
        writer.write_enum_value("resourceType", self.resource_type)
        writer.write_additional_data_value(self.additional_data)
    

