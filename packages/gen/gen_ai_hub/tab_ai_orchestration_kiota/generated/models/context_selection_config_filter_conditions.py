from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .context_selection_config_filter_conditions_member1 import ContextSelectionConfig_filterConditionsMember1
    from .filter_condition import FilterCondition
    from .filter_conditions import FilterConditions

@dataclass
class ContextSelectionConfig_filterConditions(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes ContextSelectionConfig_filterConditionsMember1, FilterCondition, FilterConditions
    """
    # Composed type representation for type ContextSelectionConfig_filterConditionsMember1
    context_selection_config_filter_conditions_member1: Optional[ContextSelectionConfig_filterConditionsMember1] = None
    # Composed type representation for type FilterCondition
    filter_condition: Optional[FilterCondition] = None
    # Composed type representation for type FilterConditions
    filter_conditions: Optional[FilterConditions] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ContextSelectionConfig_filterConditions:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ContextSelectionConfig_filterConditions
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = ContextSelectionConfig_filterConditions()
        from .context_selection_config_filter_conditions_member1 import ContextSelectionConfig_filterConditionsMember1

        result.context_selection_config_filter_conditions_member1 = ContextSelectionConfig_filterConditionsMember1()
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
        from .context_selection_config_filter_conditions_member1 import ContextSelectionConfig_filterConditionsMember1
        from .filter_condition import FilterCondition
        from .filter_conditions import FilterConditions

        if self.context_selection_config_filter_conditions_member1 or self.filter_condition or self.filter_conditions:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.context_selection_config_filter_conditions_member1, self.filter_condition, self.filter_conditions)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_object_value(None, self.context_selection_config_filter_conditions_member1, self.filter_condition, self.filter_conditions)
    

