from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .vector_per_filter_search_result import VectorPerFilterSearchResult

@dataclass
class VectorSearchResults(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # List of returned results.
    results: Optional[list[VectorPerFilterSearchResult]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VectorSearchResults:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VectorSearchResults
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VectorSearchResults()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .vector_per_filter_search_result import VectorPerFilterSearchResult

        from .vector_per_filter_search_result import VectorPerFilterSearchResult

        fields: dict[str, Callable[[Any], None]] = {
            "results": lambda n : setattr(self, 'results', n.get_collection_of_object_values(VectorPerFilterSearchResult)),
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
        writer.write_collection_of_object_values("results", self.results)
        writer.write_additional_data_value(self.additional_data)
    

