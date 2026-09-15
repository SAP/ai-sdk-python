from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .google_drive_resource_detail import GoogleDriveResourceDetail

@dataclass
class GoogleDriveConfigurationMinimal(Parsable):
    # The googleDrive property
    google_drive: Optional[GoogleDriveResourceDetail] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GoogleDriveConfigurationMinimal:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GoogleDriveConfigurationMinimal
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GoogleDriveConfigurationMinimal()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .google_drive_resource_detail import GoogleDriveResourceDetail

        from .google_drive_resource_detail import GoogleDriveResourceDetail

        fields: dict[str, Callable[[Any], None]] = {
            "googleDrive": lambda n : setattr(self, 'google_drive', n.get_object_value(GoogleDriveResourceDetail)),
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
        writer.write_object_value("googleDrive", self.google_drive)
    

