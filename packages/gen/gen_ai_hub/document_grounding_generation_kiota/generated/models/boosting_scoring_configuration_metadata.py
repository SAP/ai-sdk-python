from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .boosting_scoring_configuration_metadata_scope import BoostingScoringConfiguration_metadata_scope

@dataclass
class BoostingScoringConfiguration_metadata(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    from .boosting_scoring_configuration_metadata_scope import BoostingScoringConfiguration_metadata_scope

    # The scope property
    scope: Optional[BoostingScoringConfiguration_metadata_scope] = BoostingScoringConfiguration_metadata_scope("document")
    # The key property
    key: Optional[str] = None
    # The value property
    value: Optional[list[str]] = None
    # The weight property
    weight: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BoostingScoringConfiguration_metadata:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BoostingScoringConfiguration_metadata
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BoostingScoringConfiguration_metadata()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .boosting_scoring_configuration_metadata_scope import BoostingScoringConfiguration_metadata_scope

        from .boosting_scoring_configuration_metadata_scope import BoostingScoringConfiguration_metadata_scope

        fields: dict[str, Callable[[Any], None]] = {
            "key": lambda n : setattr(self, 'key', n.get_str_value()),
            "scope": lambda n : setattr(self, 'scope', n.get_enum_value(BoostingScoringConfiguration_metadata_scope)),
            "value": lambda n : setattr(self, 'value', n.get_collection_of_primitive_values(str)),
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
        writer.write_str_value("key", self.key)
        writer.write_enum_value("scope", self.scope)
        writer.write_collection_of_primitive_values("value", self.value)
        writer.write_int_value("weight", self.weight)
        writer.write_additional_data_value(self.additional_data)
    

