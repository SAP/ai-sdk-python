from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .context_selection_config_filter_conditions import ContextSelectionConfig_filterConditions
    from .context_selection_config_index_column import ContextSelectionConfig_indexColumn
    from .context_selection_config_num_rows import ContextSelectionConfig_numRows
    from .context_selection_config_strategy_config import ContextSelectionConfig_strategyConfig
    from .context_selection_strategy_enum import ContextSelectionStrategyEnum

@dataclass
class ContextSelectionConfig(AdditionalDataHolder, Parsable):
    """
    Configuration for context selection.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    from .context_selection_strategy_enum import ContextSelectionStrategyEnum

    # Sampling strategy for context selection.
    strategy: Optional[ContextSelectionStrategyEnum] = ContextSelectionStrategyEnum("random")
    # Filter conditions for context selection
    filter_conditions: Optional[ContextSelectionConfig_filterConditions] = None
    # Name of the unique row-identifier column (e.g. 'ROW_INDEX'). Required for 'heuristic', and deterministic 'random' strategies.
    index_column: Optional[ContextSelectionConfig_indexColumn] = None
    # Number of rows to select for context. If not provided or set to 0, context selection is skipped.
    num_rows: Optional[ContextSelectionConfig_numRows] = None
    # Strategy-specific configuration parameters.
    strategy_config: Optional[ContextSelectionConfig_strategyConfig] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ContextSelectionConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ContextSelectionConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ContextSelectionConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .context_selection_config_filter_conditions import ContextSelectionConfig_filterConditions
        from .context_selection_config_index_column import ContextSelectionConfig_indexColumn
        from .context_selection_config_num_rows import ContextSelectionConfig_numRows
        from .context_selection_config_strategy_config import ContextSelectionConfig_strategyConfig
        from .context_selection_strategy_enum import ContextSelectionStrategyEnum

        from .context_selection_config_filter_conditions import ContextSelectionConfig_filterConditions
        from .context_selection_config_index_column import ContextSelectionConfig_indexColumn
        from .context_selection_config_num_rows import ContextSelectionConfig_numRows
        from .context_selection_config_strategy_config import ContextSelectionConfig_strategyConfig
        from .context_selection_strategy_enum import ContextSelectionStrategyEnum

        fields: dict[str, Callable[[Any], None]] = {
            "filterConditions": lambda n : setattr(self, 'filter_conditions', n.get_object_value(ContextSelectionConfig_filterConditions)),
            "indexColumn": lambda n : setattr(self, 'index_column', n.get_object_value(ContextSelectionConfig_indexColumn)),
            "numRows": lambda n : setattr(self, 'num_rows', n.get_object_value(ContextSelectionConfig_numRows)),
            "strategy": lambda n : setattr(self, 'strategy', n.get_enum_value(ContextSelectionStrategyEnum)),
            "strategyConfig": lambda n : setattr(self, 'strategy_config', n.get_object_value(ContextSelectionConfig_strategyConfig)),
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
        writer.write_object_value("filterConditions", self.filter_conditions)
        writer.write_object_value("indexColumn", self.index_column)
        writer.write_object_value("numRows", self.num_rows)
        writer.write_enum_value("strategy", self.strategy)
        writer.write_object_value("strategyConfig", self.strategy_config)
        writer.write_additional_data_value(self.additional_data)
    

