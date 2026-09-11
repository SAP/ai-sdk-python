from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .documents_chunk import DocumentsChunk

@dataclass
class VectorPerFilterSearchResult(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The filterId property
    filter_id: Optional[str] = None
    # The results property
    results: Optional[list[DocumentsChunk]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VectorPerFilterSearchResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VectorPerFilterSearchResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VectorPerFilterSearchResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .documents_chunk import DocumentsChunk

        from .documents_chunk import DocumentsChunk

        fields: dict[str, Callable[[Any], None]] = {
            "filterId": lambda n : setattr(self, 'filter_id', n.get_str_value()),
            "results": lambda n : setattr(self, 'results', n.get_collection_of_object_values(DocumentsChunk)),
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
        writer.write_str_value("filterId", self.filter_id)
        writer.write_collection_of_object_values("results", self.results)
        writer.write_additional_data_value(self.additional_data)
    

