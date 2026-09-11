from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .columnar_data import ColumnarData
    from .context_selection_config import ContextSelectionConfig
    from .prediction_config import PredictionConfig
    from .predict_request_context_rows import PredictRequest_contextRows
    from .predict_request_model_config import PredictRequest_modelConfig
    from .predict_request_rows import PredictRequest_rows
    from .t_f_m_enum import TFMEnum

@dataclass
class PredictRequest(AdditionalDataHolder, Parsable):
    """
    Request schema for prediction endpoint.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Query-only rows in columnar form. An object mapping from column name to array of column values.
    columns: Optional[ColumnarData] = None
    # (Optional) Context rows in columnar form, only relevant if 'columns' is provided. An object mapping from column name to array of column values.
    context_columns: Optional[ColumnarData] = None
    # (Optional) Context rows in row form, only relevant if 'rows' is provided. An array of objects representing table rows.
    context_rows: Optional[PredictRequest_contextRows] = None
    # Context selection configuration
    context_selection_config: Optional[ContextSelectionConfig] = None
    # (Optional) Any additional TFM-specific configurations that will be passed to the selected TFM.
    model_config: Optional[PredictRequest_modelConfig] = None
    # Name of the deployed model
    model_name: Optional[TFMEnum] = None
    # Prediction configuration
    prediction_config: Optional[PredictionConfig] = None
    # Query-only rows in row form. An array of objects representing table rows.
    rows: Optional[PredictRequest_rows] = None
    # Scenario configuration identifier
    scenario_config_name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PredictRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PredictRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PredictRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .columnar_data import ColumnarData
        from .context_selection_config import ContextSelectionConfig
        from .prediction_config import PredictionConfig
        from .predict_request_context_rows import PredictRequest_contextRows
        from .predict_request_model_config import PredictRequest_modelConfig
        from .predict_request_rows import PredictRequest_rows
        from .t_f_m_enum import TFMEnum

        from .columnar_data import ColumnarData
        from .context_selection_config import ContextSelectionConfig
        from .prediction_config import PredictionConfig
        from .predict_request_context_rows import PredictRequest_contextRows
        from .predict_request_model_config import PredictRequest_modelConfig
        from .predict_request_rows import PredictRequest_rows
        from .t_f_m_enum import TFMEnum

        fields: dict[str, Callable[[Any], None]] = {
            "columns": lambda n : setattr(self, 'columns', n.get_object_value(ColumnarData)),
            "contextColumns": lambda n : setattr(self, 'context_columns', n.get_object_value(ColumnarData)),
            "contextRows": lambda n : setattr(self, 'context_rows', n.get_object_value(PredictRequest_contextRows)),
            "contextSelectionConfig": lambda n : setattr(self, 'context_selection_config', n.get_object_value(ContextSelectionConfig)),
            "modelConfig": lambda n : setattr(self, 'model_config', n.get_object_value(PredictRequest_modelConfig)),
            "modelName": lambda n : setattr(self, 'model_name', n.get_enum_value(TFMEnum)),
            "predictionConfig": lambda n : setattr(self, 'prediction_config', n.get_object_value(PredictionConfig)),
            "rows": lambda n : setattr(self, 'rows', n.get_object_value(PredictRequest_rows)),
            "scenarioConfigName": lambda n : setattr(self, 'scenario_config_name', n.get_str_value()),
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
        writer.write_object_value("columns", self.columns)
        writer.write_object_value("contextColumns", self.context_columns)
        writer.write_object_value("contextRows", self.context_rows)
        writer.write_object_value("contextSelectionConfig", self.context_selection_config)
        writer.write_object_value("modelConfig", self.model_config)
        writer.write_enum_value("modelName", self.model_name)
        writer.write_object_value("predictionConfig", self.prediction_config)
        writer.write_object_value("rows", self.rows)
        writer.write_str_value("scenarioConfigName", self.scenario_config_name)
        writer.write_additional_data_value(self.additional_data)
    

