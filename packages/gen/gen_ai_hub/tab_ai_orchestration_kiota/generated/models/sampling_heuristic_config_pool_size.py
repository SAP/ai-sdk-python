from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .sampling_heuristic_config_pool_size_member1 import SamplingHeuristicConfig_poolSizeMember1

@dataclass
class SamplingHeuristicConfig_poolSize(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes int, SamplingHeuristicConfig_poolSizeMember1
    """
    # Composed type representation for type int
    integer: Optional[int] = None
    # Composed type representation for type SamplingHeuristicConfig_poolSizeMember1
    sampling_heuristic_config_pool_size_member1: Optional[SamplingHeuristicConfig_poolSizeMember1] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SamplingHeuristicConfig_poolSize:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SamplingHeuristicConfig_poolSize
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = SamplingHeuristicConfig_poolSize()
        if integer_value := parse_node.get_int_value():
            result.integer = integer_value
        else:
            from .sampling_heuristic_config_pool_size_member1 import SamplingHeuristicConfig_poolSizeMember1

            result.sampling_heuristic_config_pool_size_member1 = SamplingHeuristicConfig_poolSizeMember1()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .sampling_heuristic_config_pool_size_member1 import SamplingHeuristicConfig_poolSizeMember1

        if self.sampling_heuristic_config_pool_size_member1:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.sampling_heuristic_config_pool_size_member1)
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
            writer.write_object_value(None, self.sampling_heuristic_config_pool_size_member1)
    

