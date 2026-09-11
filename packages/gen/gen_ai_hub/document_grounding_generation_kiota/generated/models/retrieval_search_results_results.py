from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieval_per_filter_search_result import RetrievalPerFilterSearchResult
    from .retrieval_per_filter_search_result_with_error import RetrievalPerFilterSearchResultWithError

@dataclass
class RetrievalSearchResults_results(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes RetrievalPerFilterSearchResult, RetrievalPerFilterSearchResultWithError
    """
    # Composed type representation for type RetrievalPerFilterSearchResult
    retrieval_per_filter_search_result: Optional[RetrievalPerFilterSearchResult] = None
    # Composed type representation for type RetrievalPerFilterSearchResultWithError
    retrieval_per_filter_search_result_with_error: Optional[RetrievalPerFilterSearchResultWithError] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalSearchResults_results:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalSearchResults_results
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = RetrievalSearchResults_results()
        from .retrieval_per_filter_search_result import RetrievalPerFilterSearchResult

        result.retrieval_per_filter_search_result = RetrievalPerFilterSearchResult()
        from .retrieval_per_filter_search_result_with_error import RetrievalPerFilterSearchResultWithError

        result.retrieval_per_filter_search_result_with_error = RetrievalPerFilterSearchResultWithError()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieval_per_filter_search_result import RetrievalPerFilterSearchResult
        from .retrieval_per_filter_search_result_with_error import RetrievalPerFilterSearchResultWithError

        if self.retrieval_per_filter_search_result or self.retrieval_per_filter_search_result_with_error:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.retrieval_per_filter_search_result, self.retrieval_per_filter_search_result_with_error)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_object_value(None, self.retrieval_per_filter_search_result, self.retrieval_per_filter_search_result_with_error)
    

