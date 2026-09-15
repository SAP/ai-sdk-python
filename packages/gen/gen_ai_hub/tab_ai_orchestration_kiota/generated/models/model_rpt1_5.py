from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .model_rpt1_5_index_column import ModelRpt1_5_index_column
    from .model_rpt1_5_prediction_config import ModelRpt1_5PredictionConfig

@dataclass
class ModelRpt1_5(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # (Optional, RPT Default: True) Relevant when data_schema isn't passed. Whether or not to parse data types, such as interpreting strings as numbers or dates.
    parse_data_types: Optional[bool] = True
    # (Optional) The name of the column used to identify the row. This column isn't used as an input feature for the model, and is returned in the response objects.
    index_column: Optional[ModelRpt1_5_index_column] = None
    # (Optional) An object for configuring predictions.
    prediction_config: Optional[ModelRpt1_5PredictionConfig] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ModelRpt1_5:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ModelRpt1_5
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ModelRpt1_5()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .model_rpt1_5_index_column import ModelRpt1_5_index_column
        from .model_rpt1_5_prediction_config import ModelRpt1_5PredictionConfig

        from .model_rpt1_5_index_column import ModelRpt1_5_index_column
        from .model_rpt1_5_prediction_config import ModelRpt1_5PredictionConfig

        fields: dict[str, Callable[[Any], None]] = {
            "index_column": lambda n : setattr(self, 'index_column', n.get_object_value(ModelRpt1_5_index_column)),
            "parse_data_types": lambda n : setattr(self, 'parse_data_types', n.get_bool_value()),
            "prediction_config": lambda n : setattr(self, 'prediction_config', n.get_object_value(ModelRpt1_5PredictionConfig)),
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
        writer.write_object_value("index_column", self.index_column)
        writer.write_bool_value("parse_data_types", self.parse_data_types)
        writer.write_object_value("prediction_config", self.prediction_config)
        writer.write_additional_data_value(self.additional_data)
    

