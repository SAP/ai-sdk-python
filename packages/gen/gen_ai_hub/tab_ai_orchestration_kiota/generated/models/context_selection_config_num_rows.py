from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .context_selection_config_num_rows_member1 import ContextSelectionConfig_numRowsMember1

@dataclass
class ContextSelectionConfig_numRows(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes ContextSelectionConfig_numRowsMember1, int
    """
    # Composed type representation for type ContextSelectionConfig_numRowsMember1
    context_selection_config_num_rows_member1: Optional[ContextSelectionConfig_numRowsMember1] = None
    # Composed type representation for type int
    integer: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ContextSelectionConfig_numRows:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ContextSelectionConfig_numRows
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = ContextSelectionConfig_numRows()
        if integer_value := parse_node.get_int_value():
            result.integer = integer_value
        else:
            from .context_selection_config_num_rows_member1 import ContextSelectionConfig_numRowsMember1

            result.context_selection_config_num_rows_member1 = ContextSelectionConfig_numRowsMember1()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .context_selection_config_num_rows_member1 import ContextSelectionConfig_numRowsMember1

        if self.context_selection_config_num_rows_member1:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.context_selection_config_num_rows_member1)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.integer:
            writer.write_int_value(None, self.integer)
        else:
            writer.write_object_value(None, self.context_selection_config_num_rows_member1)
    

