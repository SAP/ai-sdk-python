from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .predict_metadata import PredictMetadata
    from .predict_response_predictions import PredictResponse_predictions
    from .predict_status import PredictStatus

@dataclass
class PredictResponse(AdditionalDataHolder, Parsable):
    """
    Response schema for prediction endpoint.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Warnings or informational messages from context selection
    additional_information: Optional[list[str]] = None
    # The id property
    id: Optional[str] = None
    # Metadata about the prediction.
    metadata: Optional[PredictMetadata] = None
    # The predictions property
    predictions: Optional[list[PredictResponse_predictions]] = None
    # Status of the prediction.
    status: Optional[PredictStatus] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PredictResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PredictResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PredictResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .predict_metadata import PredictMetadata
        from .predict_response_predictions import PredictResponse_predictions
        from .predict_status import PredictStatus

        from .predict_metadata import PredictMetadata
        from .predict_response_predictions import PredictResponse_predictions
        from .predict_status import PredictStatus

        fields: dict[str, Callable[[Any], None]] = {
            "additional_information": lambda n : setattr(self, 'additional_information', n.get_collection_of_primitive_values(str)),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "metadata": lambda n : setattr(self, 'metadata', n.get_object_value(PredictMetadata)),
            "predictions": lambda n : setattr(self, 'predictions', n.get_collection_of_object_values(PredictResponse_predictions)),
            "status": lambda n : setattr(self, 'status', n.get_object_value(PredictStatus)),
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
        writer.write_collection_of_primitive_values("additional_information", self.additional_information)
        writer.write_str_value("id", self.id)
        writer.write_object_value("metadata", self.metadata)
        writer.write_collection_of_object_values("predictions", self.predictions)
        writer.write_object_value("status", self.status)
        writer.write_additional_data_value(self.additional_data)
    

