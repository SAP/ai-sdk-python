from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .model_rpt1_5_explanations_top_relevant_context_rows_member1 import ModelRpt1_5Explanations_top_relevant_context_rowsMember1

@dataclass
class ModelRpt1_5Explanations_top_relevant_context_rows(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes int, ModelRpt1_5Explanations_top_relevant_context_rowsMember1
    """
    # Composed type representation for type int
    integer: Optional[int] = None
    # Composed type representation for type ModelRpt1_5Explanations_top_relevant_context_rowsMember1
    model_rpt1_5_explanations_top_relevant_context_rows_member1: Optional[ModelRpt1_5Explanations_top_relevant_context_rowsMember1] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ModelRpt1_5Explanations_top_relevant_context_rows:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ModelRpt1_5Explanations_top_relevant_context_rows
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = ModelRpt1_5Explanations_top_relevant_context_rows()
        if integer_value := parse_node.get_int_value():
            result.integer = integer_value
        else:
            from .model_rpt1_5_explanations_top_relevant_context_rows_member1 import ModelRpt1_5Explanations_top_relevant_context_rowsMember1

            result.model_rpt1_5_explanations_top_relevant_context_rows_member1 = ModelRpt1_5Explanations_top_relevant_context_rowsMember1()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .model_rpt1_5_explanations_top_relevant_context_rows_member1 import ModelRpt1_5Explanations_top_relevant_context_rowsMember1

        if self.model_rpt1_5_explanations_top_relevant_context_rows_member1:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.model_rpt1_5_explanations_top_relevant_context_rows_member1)
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
            writer.write_object_value(None, self.model_rpt1_5_explanations_top_relevant_context_rows_member1)
    

