from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .text_only_base_chunk_create import TextOnlyBaseChunkCreate
    from .vector_document_key_value_list_pair import VectorDocumentKeyValueListPair

@dataclass
class BaseDocument(AdditionalDataHolder, Parsable):
    """
    Base class for documents, document requests and responses.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The chunks property
    chunks: Optional[list[TextOnlyBaseChunkCreate]] = None
    # The metadata property
    metadata: Optional[list[VectorDocumentKeyValueListPair]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BaseDocument:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BaseDocument
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BaseDocument()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .text_only_base_chunk_create import TextOnlyBaseChunkCreate
        from .vector_document_key_value_list_pair import VectorDocumentKeyValueListPair

        from .text_only_base_chunk_create import TextOnlyBaseChunkCreate
        from .vector_document_key_value_list_pair import VectorDocumentKeyValueListPair

        fields: dict[str, Callable[[Any], None]] = {
            "chunks": lambda n : setattr(self, 'chunks', n.get_collection_of_object_values(TextOnlyBaseChunkCreate)),
            "metadata": lambda n : setattr(self, 'metadata', n.get_collection_of_object_values(VectorDocumentKeyValueListPair)),
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
        writer.write_collection_of_object_values("chunks", self.chunks)
        writer.write_collection_of_object_values("metadata", self.metadata)
        writer.write_additional_data_value(self.additional_data)
    

