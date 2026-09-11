from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .metadata_operation import MetadataOperation

@dataclass
class MetadataKeyUpdate(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Key to update
    key: Optional[str] = None
    # Update operation executed for the key
    operations: Optional[list[MetadataOperation]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MetadataKeyUpdate:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MetadataKeyUpdate
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MetadataKeyUpdate()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .metadata_operation import MetadataOperation

        from .metadata_operation import MetadataOperation

        fields: dict[str, Callable[[Any], None]] = {
            "key": lambda n : setattr(self, 'key', n.get_str_value()),
            "operations": lambda n : setattr(self, 'operations', n.get_collection_of_object_values(MetadataOperation)),
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
        writer.write_collection_of_object_values("operations", self.operations)
        writer.write_additional_data_value(self.additional_data)
    

