from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .binary_boolean_filter_left import BinaryBooleanFilter_left
    from .binary_boolean_filter_operator import BinaryBooleanFilter_operator
    from .binary_boolean_filter_right import BinaryBooleanFilter_right

@dataclass
class BinaryBooleanFilter(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Left operand of the boolean expression
    left: Optional[BinaryBooleanFilter_left] = None
    # Boolean operator for combining filter conditions
    operator: Optional[BinaryBooleanFilter_operator] = None
    # Right operand of the boolean expression
    right: Optional[BinaryBooleanFilter_right] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BinaryBooleanFilter:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BinaryBooleanFilter
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BinaryBooleanFilter()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .binary_boolean_filter_left import BinaryBooleanFilter_left
        from .binary_boolean_filter_operator import BinaryBooleanFilter_operator
        from .binary_boolean_filter_right import BinaryBooleanFilter_right

        from .binary_boolean_filter_left import BinaryBooleanFilter_left
        from .binary_boolean_filter_operator import BinaryBooleanFilter_operator
        from .binary_boolean_filter_right import BinaryBooleanFilter_right

        fields: dict[str, Callable[[Any], None]] = {
            "left": lambda n : setattr(self, 'left', n.get_object_value(BinaryBooleanFilter_left)),
            "operator": lambda n : setattr(self, 'operator', n.get_enum_value(BinaryBooleanFilter_operator)),
            "right": lambda n : setattr(self, 'right', n.get_object_value(BinaryBooleanFilter_right)),
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
        writer.write_object_value("left", self.left)
        writer.write_enum_value("operator", self.operator)
        writer.write_object_value("right", self.right)
        writer.write_additional_data_value(self.additional_data)
    

