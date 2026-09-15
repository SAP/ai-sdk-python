from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .document_metadata_match_mode import DocumentMetadata_matchMode

@dataclass
class DocumentMetadata(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Metadata key name.
    key: Optional[str] = None
    # Match mode for the metadata key (ANY or ALL).
    match_mode: Optional[DocumentMetadata_matchMode] = None
    # An array of string values associated with the metadata key. If the key already exists, its values will be overwritten. Setting the value to null will delete the metadata key-value pair.
    value: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DocumentMetadata:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DocumentMetadata
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DocumentMetadata()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .document_metadata_match_mode import DocumentMetadata_matchMode

        from .document_metadata_match_mode import DocumentMetadata_matchMode

        fields: dict[str, Callable[[Any], None]] = {
            "key": lambda n : setattr(self, 'key', n.get_str_value()),
            "matchMode": lambda n : setattr(self, 'match_mode', n.get_enum_value(DocumentMetadata_matchMode)),
            "value": lambda n : setattr(self, 'value', n.get_collection_of_primitive_values(str)),
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
        writer.write_str_value("key", self.key)
        writer.write_enum_value("matchMode", self.match_mode)
        writer.write_collection_of_primitive_values("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

