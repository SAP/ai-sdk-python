from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .post_processing_object_reference import PostProcessingObjectReference
    from .post_processing_operation import PostProcessingOperation

@dataclass
class PostProcessingOperation_inputs(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes PostProcessingObjectReference, PostProcessingOperation
    """
    # Composed type representation for type PostProcessingObjectReference
    post_processing_object_reference: Optional[PostProcessingObjectReference] = None
    # Composed type representation for type PostProcessingOperation
    post_processing_operation: Optional[PostProcessingOperation] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PostProcessingOperation_inputs:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PostProcessingOperation_inputs
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = PostProcessingOperation_inputs()
        if mapping_value and mapping_value.casefold() == "PostProcessingObjectReference".casefold():
            from .post_processing_object_reference import PostProcessingObjectReference

            result.post_processing_object_reference = PostProcessingObjectReference()
        elif mapping_value and mapping_value.casefold() == "PostProcessingOperation".casefold():
            from .post_processing_operation import PostProcessingOperation

            result.post_processing_operation = PostProcessingOperation()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .post_processing_object_reference import PostProcessingObjectReference
        from .post_processing_operation import PostProcessingOperation

        if self.post_processing_object_reference:
            return self.post_processing_object_reference.get_field_deserializers()
        if self.post_processing_operation:
            return self.post_processing_operation.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.post_processing_object_reference:
            writer.write_object_value(None, self.post_processing_object_reference)
        elif self.post_processing_operation:
            writer.write_object_value(None, self.post_processing_operation)
    

