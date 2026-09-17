from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieval_search_input_filters import RetrievalSearchInput_filters
    from .retrieval_search_input_post_processing import RetrievalSearchInput_postProcessing

@dataclass
class RetrievalSearchInput(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The filters property
    filters: Optional[list[RetrievalSearchInput_filters]] = None
    # List of operations to be performed across PerFilterSearchResults.
    post_processing: Optional[list[RetrievalSearchInput_postProcessing]] = None
    # Query string
    query: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalSearchInput:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalSearchInput
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrievalSearchInput()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieval_search_input_filters import RetrievalSearchInput_filters
        from .retrieval_search_input_post_processing import RetrievalSearchInput_postProcessing

        from .retrieval_search_input_filters import RetrievalSearchInput_filters
        from .retrieval_search_input_post_processing import RetrievalSearchInput_postProcessing

        fields: dict[str, Callable[[Any], None]] = {
            "filters": lambda n : setattr(self, 'filters', n.get_collection_of_object_values(RetrievalSearchInput_filters)),
            "postProcessing": lambda n : setattr(self, 'post_processing', n.get_collection_of_object_values(RetrievalSearchInput_postProcessing)),
            "query": lambda n : setattr(self, 'query', n.get_str_value()),
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
        writer.write_collection_of_object_values("filters", self.filters)
        writer.write_collection_of_object_values("postProcessing", self.post_processing)
        writer.write_str_value("query", self.query)
        writer.write_additional_data_value(self.additional_data)
    

