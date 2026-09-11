from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .configuration_document_type import ConfigurationDocument_type
    from .document_metadata import DocumentMetadata

@dataclass
class ConfigurationDocument(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Absolute file path of the document in the repository.
    absolute_file_path: Optional[str] = None
    # UTC timestamp when the document was created (RFC 3339 format, e.g., 2025-08-28T06:15:30Z)
    created_timestamp: Optional[datetime.datetime] = None
    # Unique identifier for the document.
    id: Optional[str] = None
    # Metadata key-value pairs associated with the document.
    metadata: Optional[list[DocumentMetadata]] = None
    # Title of the document.
    title: Optional[str] = None
    # Type of the resource. Can be FOLDER, DOCUMENT.
    type: Optional[ConfigurationDocument_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ConfigurationDocument:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ConfigurationDocument
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ConfigurationDocument()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .configuration_document_type import ConfigurationDocument_type
        from .document_metadata import DocumentMetadata

        from .configuration_document_type import ConfigurationDocument_type
        from .document_metadata import DocumentMetadata

        fields: dict[str, Callable[[Any], None]] = {
            "absoluteFilePath": lambda n : setattr(self, 'absolute_file_path', n.get_str_value()),
            "createdTimestamp": lambda n : setattr(self, 'created_timestamp', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "metadata": lambda n : setattr(self, 'metadata', n.get_collection_of_object_values(DocumentMetadata)),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(ConfigurationDocument_type)),
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
        writer.write_str_value("absoluteFilePath", self.absolute_file_path)
        writer.write_datetime_value("createdTimestamp", self.created_timestamp)
        writer.write_str_value("id", self.id)
        writer.write_collection_of_object_values("metadata", self.metadata)
        writer.write_str_value("title", self.title)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

