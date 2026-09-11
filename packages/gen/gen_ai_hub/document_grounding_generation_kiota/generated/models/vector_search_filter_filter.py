from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .binary_boolean_filter import BinaryBooleanFilter
    from .scoped_key_value_list_pair import ScopedKeyValueListPair

@dataclass
class VectorSearchFilter_filter(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes BinaryBooleanFilter, ScopedKeyValueListPair
    """
    # Composed type representation for type BinaryBooleanFilter
    binary_boolean_filter: Optional[BinaryBooleanFilter] = None
    # Composed type representation for type ScopedKeyValueListPair
    scoped_key_value_list_pair: Optional[ScopedKeyValueListPair] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VectorSearchFilter_filter:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VectorSearchFilter_filter
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = VectorSearchFilter_filter()
        from .binary_boolean_filter import BinaryBooleanFilter

        result.binary_boolean_filter = BinaryBooleanFilter()
        from .scoped_key_value_list_pair import ScopedKeyValueListPair

        result.scoped_key_value_list_pair = ScopedKeyValueListPair()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .binary_boolean_filter import BinaryBooleanFilter
        from .scoped_key_value_list_pair import ScopedKeyValueListPair

        if self.binary_boolean_filter or self.scoped_key_value_list_pair:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.binary_boolean_filter, self.scoped_key_value_list_pair)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_object_value(None, self.binary_boolean_filter, self.scoped_key_value_list_pair)
    

