from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class DocumentsStatusResponse_resources(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The absoluteUrl property
    absolute_url: Optional[str] = None
    # The createdTimestamp property
    created_timestamp: Optional[str] = None
    # The downloadLocation property
    download_location: Optional[str] = None
    # The id property
    id: Optional[str] = None
    # The lastUpdatedTimestamp property
    last_updated_timestamp: Optional[str] = None
    # The metadataId property
    metadata_id: Optional[str] = None
    # The status property
    status: Optional[str] = None
    # The title property
    title: Optional[str] = None
    # The viewLocation property
    view_location: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DocumentsStatusResponse_resources:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DocumentsStatusResponse_resources
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DocumentsStatusResponse_resources()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "absoluteUrl": lambda n : setattr(self, 'absolute_url', n.get_str_value()),
            "createdTimestamp": lambda n : setattr(self, 'created_timestamp', n.get_str_value()),
            "downloadLocation": lambda n : setattr(self, 'download_location', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "lastUpdatedTimestamp": lambda n : setattr(self, 'last_updated_timestamp', n.get_str_value()),
            "metadataId": lambda n : setattr(self, 'metadata_id', n.get_str_value()),
            "status": lambda n : setattr(self, 'status', n.get_str_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "viewLocation": lambda n : setattr(self, 'view_location', n.get_str_value()),
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
        writer.write_str_value("absoluteUrl", self.absolute_url)
        writer.write_str_value("createdTimestamp", self.created_timestamp)
        writer.write_str_value("downloadLocation", self.download_location)
        writer.write_str_value("id", self.id)
        writer.write_str_value("lastUpdatedTimestamp", self.last_updated_timestamp)
        writer.write_str_value("metadataId", self.metadata_id)
        writer.write_str_value("status", self.status)
        writer.write_str_value("title", self.title)
        writer.write_str_value("viewLocation", self.view_location)
        writer.write_additional_data_value(self.additional_data)
    

