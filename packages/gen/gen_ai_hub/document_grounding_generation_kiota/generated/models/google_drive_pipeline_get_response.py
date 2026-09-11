from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .base_pipeline_response import BasePipelineResponse
    from .google_drive_configuration_minimal import GoogleDriveConfigurationMinimal

from .base_pipeline_response import BasePipelineResponse

@dataclass
class GoogleDrivePipelineGetResponse(BasePipelineResponse, Parsable):
    # The configuration property
    configuration: Optional[GoogleDriveConfigurationMinimal] = None
    # The type property
    type: Optional[GoogleDrivePipelineGetResponse_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GoogleDrivePipelineGetResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GoogleDrivePipelineGetResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GoogleDrivePipelineGetResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .base_pipeline_response import BasePipelineResponse
        from .google_drive_configuration_minimal import GoogleDriveConfigurationMinimal

        from .base_pipeline_response import BasePipelineResponse
        from .google_drive_configuration_minimal import GoogleDriveConfigurationMinimal

        fields: dict[str, Callable[[Any], None]] = {
            "configuration": lambda n : setattr(self, 'configuration', n.get_object_value(GoogleDriveConfigurationMinimal)),
        }
        super_fields = super().get_field_deserializers()
        fields.update(super_fields)
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        super().serialize(writer)
        writer.write_object_value("configuration", self.configuration)
    

