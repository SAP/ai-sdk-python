from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .target_column import TargetColumn

@dataclass
class PredictionConfig(Parsable):
    """
    Configuration for what to predict.Model-agnostic prediction config. Only contains fields shared acrossall TFMs. Model-specific fields belong in `PredictRequest.modelConfig`.
    """
    # List of target columns with prediction configuration
    target_columns: Optional[list[TargetColumn]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PredictionConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PredictionConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PredictionConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .target_column import TargetColumn

        from .target_column import TargetColumn

        fields: dict[str, Callable[[Any], None]] = {
            "targetColumns": lambda n : setattr(self, 'target_columns', n.get_collection_of_object_values(TargetColumn)),
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
        writer.write_collection_of_object_values("targetColumns", self.target_columns)
    

