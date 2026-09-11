from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .vector_key_value_list_pair import VectorKeyValueListPair

@dataclass
class TextOnlyBaseChunk(AdditionalDataHolder, Parsable):
    """
    Schema for a text-only chunk.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The content property
    content: Optional[str] = None
    # Unique identifier of a chuk.
    id: Optional[UUID] = None
    # The metadata property
    metadata: Optional[list[VectorKeyValueListPair]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TextOnlyBaseChunk:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TextOnlyBaseChunk
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TextOnlyBaseChunk()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .vector_key_value_list_pair import VectorKeyValueListPair

        from .vector_key_value_list_pair import VectorKeyValueListPair

        fields: dict[str, Callable[[Any], None]] = {
            "content": lambda n : setattr(self, 'content', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "metadata": lambda n : setattr(self, 'metadata', n.get_collection_of_object_values(VectorKeyValueListPair)),
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
        writer.write_str_value("content", self.content)
        writer.write_uuid_value("id", self.id)
        writer.write_collection_of_object_values("metadata", self.metadata)
        writer.write_additional_data_value(self.additional_data)
    

