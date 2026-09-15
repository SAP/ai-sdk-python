from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .context_selection_config_strategy_config_member1 import ContextSelectionConfig_strategyConfigMember1
    from .sampling_heuristic_config import SamplingHeuristicConfig
    from .sampling_random_config import SamplingRandomConfig

@dataclass
class ContextSelectionConfig_strategyConfig(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes ContextSelectionConfig_strategyConfigMember1, SamplingHeuristicConfig, SamplingRandomConfig
    """
    # Composed type representation for type ContextSelectionConfig_strategyConfigMember1
    context_selection_config_strategy_config_member1: Optional[ContextSelectionConfig_strategyConfigMember1] = None
    # Composed type representation for type SamplingHeuristicConfig
    sampling_heuristic_config: Optional[SamplingHeuristicConfig] = None
    # Composed type representation for type SamplingRandomConfig
    sampling_random_config: Optional[SamplingRandomConfig] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ContextSelectionConfig_strategyConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ContextSelectionConfig_strategyConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = ContextSelectionConfig_strategyConfig()
        from .context_selection_config_strategy_config_member1 import ContextSelectionConfig_strategyConfigMember1

        result.context_selection_config_strategy_config_member1 = ContextSelectionConfig_strategyConfigMember1()
        from .sampling_heuristic_config import SamplingHeuristicConfig

        result.sampling_heuristic_config = SamplingHeuristicConfig()
        from .sampling_random_config import SamplingRandomConfig

        result.sampling_random_config = SamplingRandomConfig()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .context_selection_config_strategy_config_member1 import ContextSelectionConfig_strategyConfigMember1
        from .sampling_heuristic_config import SamplingHeuristicConfig
        from .sampling_random_config import SamplingRandomConfig

        if self.context_selection_config_strategy_config_member1 or self.sampling_heuristic_config or self.sampling_random_config:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.context_selection_config_strategy_config_member1, self.sampling_heuristic_config, self.sampling_random_config)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_object_value(None, self.context_selection_config_strategy_config_member1, self.sampling_heuristic_config, self.sampling_random_config)
    

