from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .predict_request_context_rows_member1 import PredictRequest_contextRowsMember1
    from .predict_request_context_rows_member2 import PredictRequest_contextRowsMember2

@dataclass
class PredictRequest_contextRows(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes list[PredictRequest_contextRowsMember1], PredictRequest_contextRowsMember2
    """
    # Composed type representation for type list[PredictRequest_contextRowsMember1]
    predict_request_context_rows_member1: Optional[list[PredictRequest_contextRowsMember1]] = None
    # Composed type representation for type PredictRequest_contextRowsMember2
    predict_request_context_rows_member2: Optional[PredictRequest_contextRowsMember2] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PredictRequest_contextRows:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PredictRequest_contextRows
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = PredictRequest_contextRows()
        if predict_request_context_rows_member1_value := parse_node.get_collection_of_object_values(PredictRequest_contextRowsMember1):
            result.predict_request_context_rows_member1 = predict_request_context_rows_member1_value
        else:
            from .predict_request_context_rows_member2 import PredictRequest_contextRowsMember2

            result.predict_request_context_rows_member2 = PredictRequest_contextRowsMember2()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .predict_request_context_rows_member1 import PredictRequest_contextRowsMember1
        from .predict_request_context_rows_member2 import PredictRequest_contextRowsMember2

        if self.predict_request_context_rows_member2:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.predict_request_context_rows_member2)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.predict_request_context_rows_member1:
            writer.write_collection_of_object_values(None, self.predict_request_context_rows_member1)
        else:
            writer.write_object_value(None, self.predict_request_context_rows_member2)
    

