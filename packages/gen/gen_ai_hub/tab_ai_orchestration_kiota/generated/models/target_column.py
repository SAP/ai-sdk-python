from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .target_column_top_k import TargetColumn_top_k
    from .task_type_enum import TaskTypeEnum

@dataclass
class TargetColumn(AdditionalDataHolder, Parsable):
    """
    Configuration for a target column to predict.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # (Optional) Placeholder value indicating cells to predict
    prediction_placeholder: Optional[str] = "[PREDICT]"
    from .task_type_enum import TaskTypeEnum

    # (Optional) Type of prediction task (classification or regression)
    task_type: Optional[TaskTypeEnum] = TaskTypeEnum("classification")
    # Name of the column to predict
    name: Optional[str] = None
    # (Optional) Controls how many labels to predict for each column in each row. Only applicable to 'classification' task type.
    top_k: Optional[TargetColumn_top_k] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TargetColumn:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TargetColumn
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TargetColumn()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .target_column_top_k import TargetColumn_top_k
        from .task_type_enum import TaskTypeEnum

        from .target_column_top_k import TargetColumn_top_k
        from .task_type_enum import TaskTypeEnum

        fields: dict[str, Callable[[Any], None]] = {
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "prediction_placeholder": lambda n : setattr(self, 'prediction_placeholder', n.get_str_value()),
            "task_type": lambda n : setattr(self, 'task_type', n.get_enum_value(TaskTypeEnum)),
            "top_k": lambda n : setattr(self, 'top_k', n.get_object_value(TargetColumn_top_k)),
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
        writer.write_str_value("name", self.name)
        writer.write_str_value("prediction_placeholder", self.prediction_placeholder)
        writer.write_enum_value("task_type", self.task_type)
        writer.write_object_value("top_k", self.top_k)
        writer.write_additional_data_value(self.additional_data)
    

