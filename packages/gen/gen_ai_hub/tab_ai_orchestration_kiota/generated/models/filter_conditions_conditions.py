from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .filter_condition import FilterCondition
    from .filter_conditions import FilterConditions

@dataclass
class FilterConditions_conditions(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes FilterCondition, FilterConditions
    """
    # Composed type representation for type FilterCondition
    filter_condition: Optional[FilterCondition] = None
    # Composed type representation for type FilterConditions
    filter_conditions: Optional[FilterConditions] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FilterConditions_conditions:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FilterConditions_conditions
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = FilterConditions_conditions()
        from .filter_condition import FilterCondition

        result.filter_condition = FilterCondition()
        from .filter_conditions import FilterConditions

        result.filter_conditions = FilterConditions()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .filter_condition import FilterCondition
        from .filter_conditions import FilterConditions

        if self.filter_condition or self.filter_conditions:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.filter_condition, self.filter_conditions)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_object_value(None, self.filter_condition, self.filter_conditions)
    

