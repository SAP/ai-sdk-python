from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .vector_search_filter import VectorSearchFilter

@dataclass
class TextSearchRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The filters property
    filters: Optional[list[VectorSearchFilter]] = None
    # Query string
    query: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TextSearchRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TextSearchRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TextSearchRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .vector_search_filter import VectorSearchFilter

        from .vector_search_filter import VectorSearchFilter

        fields: dict[str, Callable[[Any], None]] = {
            "filters": lambda n : setattr(self, 'filters', n.get_collection_of_object_values(VectorSearchFilter)),
            "query": lambda n : setattr(self, 'query', n.get_str_value()),
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
        writer.write_collection_of_object_values("filters", self.filters)
        writer.write_str_value("query", self.query)
        writer.write_additional_data_value(self.additional_data)
    

