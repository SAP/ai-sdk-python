from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .vector_search_select_option_enum import VectorSearchSelectOptionEnum

@dataclass
class VectorSearchDocumentKeyValueListPair(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The key property
    key: Optional[str] = None
    # Select mode for search filters
    select_mode: Optional[list[VectorSearchSelectOptionEnum]] = None
    # The value property
    value: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VectorSearchDocumentKeyValueListPair:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VectorSearchDocumentKeyValueListPair
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VectorSearchDocumentKeyValueListPair()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .vector_search_select_option_enum import VectorSearchSelectOptionEnum

        from .vector_search_select_option_enum import VectorSearchSelectOptionEnum

        fields: dict[str, Callable[[Any], None]] = {
            "key": lambda n : setattr(self, 'key', n.get_str_value()),
            "selectMode": lambda n : setattr(self, 'select_mode', n.get_collection_of_enum_values(VectorSearchSelectOptionEnum)),
            "value": lambda n : setattr(self, 'value', n.get_collection_of_primitive_values(str)),
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
        writer.write_collection_of_enum_values("selectMode", self.select_mode)
        writer.write_collection_of_primitive_values("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

