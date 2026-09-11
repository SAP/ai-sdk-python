from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class SamplingRandomConfig(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # When true, uses HASH_SHA256 of indexColumn for ordering instead of RAND(), producing the same row order on every call for the same data.
    deterministic: Optional[bool] = False
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SamplingRandomConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SamplingRandomConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SamplingRandomConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "deterministic": lambda n : setattr(self, 'deterministic', n.get_bool_value()),
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
        writer.write_bool_value("deterministic", self.deterministic)
        writer.write_additional_data_value(self.additional_data)
    

