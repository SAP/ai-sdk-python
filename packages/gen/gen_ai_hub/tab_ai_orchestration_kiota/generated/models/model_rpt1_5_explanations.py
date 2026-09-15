from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .model_rpt1_5_explanations_top_relevant_context_rows import ModelRpt1_5Explanations_top_relevant_context_rows

@dataclass
class ModelRpt1_5Explanations(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # (Optional, RPT Default: 0) Number of top column scores to return. A value of 0 disables explainability.
    top_column_scores: Optional[int] = 0
    # (Optional) Number of most relevant context rows to return for each query row.
    top_relevant_context_rows: Optional[ModelRpt1_5Explanations_top_relevant_context_rows] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ModelRpt1_5Explanations:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ModelRpt1_5Explanations
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ModelRpt1_5Explanations()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .model_rpt1_5_explanations_top_relevant_context_rows import ModelRpt1_5Explanations_top_relevant_context_rows

        from .model_rpt1_5_explanations_top_relevant_context_rows import ModelRpt1_5Explanations_top_relevant_context_rows

        fields: dict[str, Callable[[Any], None]] = {
            "top_column_scores": lambda n : setattr(self, 'top_column_scores', n.get_int_value()),
            "top_relevant_context_rows": lambda n : setattr(self, 'top_relevant_context_rows', n.get_object_value(ModelRpt1_5Explanations_top_relevant_context_rows)),
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
        writer.write_int_value("top_column_scores", self.top_column_scores)
        writer.write_object_value("top_relevant_context_rows", self.top_relevant_context_rows)
        writer.write_additional_data_value(self.additional_data)
    

