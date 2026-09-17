from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .share_point_config_get_response import SharePointConfigGetResponse

@dataclass
class MSSharePointConfigurationGetResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The destination property
    destination: Optional[str] = None
    # The sharePoint property
    share_point: Optional[SharePointConfigGetResponse] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MSSharePointConfigurationGetResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MSSharePointConfigurationGetResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MSSharePointConfigurationGetResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .share_point_config_get_response import SharePointConfigGetResponse

        from .share_point_config_get_response import SharePointConfigGetResponse

        fields: dict[str, Callable[[Any], None]] = {
            "destination": lambda n : setattr(self, 'destination', n.get_str_value()),
            "sharePoint": lambda n : setattr(self, 'share_point', n.get_object_value(SharePointConfigGetResponse)),
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
        writer.write_str_value("destination", self.destination)
        writer.write_object_value("sharePoint", self.share_point)
        writer.write_additional_data_value(self.additional_data)
    

