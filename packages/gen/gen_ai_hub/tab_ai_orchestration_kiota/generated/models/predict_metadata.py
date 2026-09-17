from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class PredictMetadata(AdditionalDataHolder, Parsable):
    """
    Metadata about the prediction.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The num_columns property
    num_columns: Optional[int] = None
    # The num_predictions property
    num_predictions: Optional[int] = None
    # The num_query_rows property
    num_query_rows: Optional[int] = None
    # The num_rows property
    num_rows: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PredictMetadata:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PredictMetadata
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PredictMetadata()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "num_columns": lambda n : setattr(self, 'num_columns', n.get_int_value()),
            "num_predictions": lambda n : setattr(self, 'num_predictions', n.get_int_value()),
            "num_query_rows": lambda n : setattr(self, 'num_query_rows', n.get_int_value()),
            "num_rows": lambda n : setattr(self, 'num_rows', n.get_int_value()),
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
        writer.write_int_value("num_columns", self.num_columns)
        writer.write_int_value("num_predictions", self.num_predictions)
        writer.write_int_value("num_query_rows", self.num_query_rows)
        writer.write_int_value("num_rows", self.num_rows)
        writer.write_additional_data_value(self.additional_data)
    

