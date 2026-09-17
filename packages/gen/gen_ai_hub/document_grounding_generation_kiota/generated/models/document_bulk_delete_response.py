from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class DocumentBulkDeleteResponse(AdditionalDataHolder, Parsable):
    """
    Response after deleting documents in bulk.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # List of successfully deleted document IDs
    deleted: Optional[list[UUID]] = None
    # List of document IDs that were not found
    not_found: Optional[list[UUID]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DocumentBulkDeleteResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DocumentBulkDeleteResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DocumentBulkDeleteResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "deleted": lambda n : setattr(self, 'deleted', n.get_collection_of_primitive_values(UUID)),
            "notFound": lambda n : setattr(self, 'not_found', n.get_collection_of_primitive_values(UUID)),
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
        writer.write_collection_of_primitive_values("deleted", self.deleted)
        writer.write_collection_of_primitive_values("notFound", self.not_found)
        writer.write_additional_data_value(self.additional_data)
    

