from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieval_binary_boolean_filter import RetrievalBinaryBooleanFilter
    from .retrieval_scoped_key_value_list_pair import RetrievalScopedKeyValueListPair

@dataclass
class RetrievalVectorSearchFilter_filter(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes RetrievalBinaryBooleanFilter, RetrievalScopedKeyValueListPair
    """
    # Composed type representation for type RetrievalBinaryBooleanFilter
    retrieval_binary_boolean_filter: Optional[RetrievalBinaryBooleanFilter] = None
    # Composed type representation for type RetrievalScopedKeyValueListPair
    retrieval_scoped_key_value_list_pair: Optional[RetrievalScopedKeyValueListPair] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalVectorSearchFilter_filter:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalVectorSearchFilter_filter
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = RetrievalVectorSearchFilter_filter()
        from .retrieval_binary_boolean_filter import RetrievalBinaryBooleanFilter

        result.retrieval_binary_boolean_filter = RetrievalBinaryBooleanFilter()
        from .retrieval_scoped_key_value_list_pair import RetrievalScopedKeyValueListPair

        result.retrieval_scoped_key_value_list_pair = RetrievalScopedKeyValueListPair()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieval_binary_boolean_filter import RetrievalBinaryBooleanFilter
        from .retrieval_scoped_key_value_list_pair import RetrievalScopedKeyValueListPair

        if self.retrieval_binary_boolean_filter or self.retrieval_scoped_key_value_list_pair:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.retrieval_binary_boolean_filter, self.retrieval_scoped_key_value_list_pair)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_object_value(None, self.retrieval_binary_boolean_filter, self.retrieval_scoped_key_value_list_pair)
    

