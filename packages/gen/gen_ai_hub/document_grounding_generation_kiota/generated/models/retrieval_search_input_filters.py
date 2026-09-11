from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieval_search_filter import RetrievalSearchFilter
    from .retrieval_vector_search_filter import RetrievalVectorSearchFilter

@dataclass
class RetrievalSearchInput_filters(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes RetrievalSearchFilter, RetrievalVectorSearchFilter
    """
    # Composed type representation for type RetrievalSearchFilter
    retrieval_search_filter: Optional[RetrievalSearchFilter] = None
    # Composed type representation for type RetrievalVectorSearchFilter
    retrieval_vector_search_filter: Optional[RetrievalVectorSearchFilter] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalSearchInput_filters:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalSearchInput_filters
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = RetrievalSearchInput_filters()
        from .retrieval_search_filter import RetrievalSearchFilter

        result.retrieval_search_filter = RetrievalSearchFilter()
        from .retrieval_vector_search_filter import RetrievalVectorSearchFilter

        result.retrieval_vector_search_filter = RetrievalVectorSearchFilter()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieval_search_filter import RetrievalSearchFilter
        from .retrieval_vector_search_filter import RetrievalVectorSearchFilter

        if self.retrieval_search_filter or self.retrieval_vector_search_filter:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.retrieval_search_filter, self.retrieval_vector_search_filter)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_object_value(None, self.retrieval_search_filter, self.retrieval_vector_search_filter)
    

