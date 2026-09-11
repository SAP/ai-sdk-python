from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class KeyWordRetrievalScoringConfiguration(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Enable dense retrieval.
    enabled: Optional[bool] = True
    # Extract Keywords from Query.
    extract_key_words_from_query: Optional[bool] = False
    # Contribution to final score.
    weight: Optional[int] = 1
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> KeyWordRetrievalScoringConfiguration:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: KeyWordRetrievalScoringConfiguration
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return KeyWordRetrievalScoringConfiguration()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "enabled": lambda n : setattr(self, 'enabled', n.get_bool_value()),
            "extractKeyWordsFromQuery": lambda n : setattr(self, 'extract_key_words_from_query', n.get_bool_value()),
            "weight": lambda n : setattr(self, 'weight', n.get_int_value()),
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
        writer.write_bool_value("enabled", self.enabled)
        writer.write_bool_value("extractKeyWordsFromQuery", self.extract_key_words_from_query)
        writer.write_int_value("weight", self.weight)
        writer.write_additional_data_value(self.additional_data)
    

