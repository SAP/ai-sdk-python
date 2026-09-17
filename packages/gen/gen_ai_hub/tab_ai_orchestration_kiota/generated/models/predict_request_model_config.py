from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .model_rpt1 import ModelRpt1
    from .model_rpt1_5 import ModelRpt1_5

@dataclass
class PredictRequest_modelConfig(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes ModelRpt1, ModelRpt1_5
    """
    # Composed type representation for type ModelRpt1
    model_rpt1: Optional[ModelRpt1] = None
    # Composed type representation for type ModelRpt1_5
    model_rpt1_5: Optional[ModelRpt1_5] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PredictRequest_modelConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PredictRequest_modelConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = PredictRequest_modelConfig()
        if mapping_value and mapping_value.casefold() == "ModelRpt1".casefold():
            from .model_rpt1 import ModelRpt1

            result.model_rpt1 = ModelRpt1()
        elif mapping_value and mapping_value.casefold() == "ModelRpt1_5".casefold():
            from .model_rpt1_5 import ModelRpt1_5

            result.model_rpt1_5 = ModelRpt1_5()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .model_rpt1 import ModelRpt1
        from .model_rpt1_5 import ModelRpt1_5

        if self.model_rpt1:
            return self.model_rpt1.get_field_deserializers()
        if self.model_rpt1_5:
            return self.model_rpt1_5.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.model_rpt1:
            writer.write_object_value(None, self.model_rpt1)
        elif self.model_rpt1_5:
            writer.write_object_value(None, self.model_rpt1_5)
    

