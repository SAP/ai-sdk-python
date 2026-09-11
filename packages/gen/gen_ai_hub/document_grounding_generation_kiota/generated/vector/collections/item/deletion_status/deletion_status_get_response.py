from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .....models.collection_deleted_response import CollectionDeletedResponse
    from .....models.collection_pending_response import CollectionPendingResponse

@dataclass
class DeletionStatusGetResponse(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes CollectionDeletedResponse, CollectionPendingResponse
    """
    # Composed type representation for type CollectionDeletedResponse
    collection_deleted_response: Optional[CollectionDeletedResponse] = None
    # Composed type representation for type CollectionPendingResponse
    collection_pending_response: Optional[CollectionPendingResponse] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DeletionStatusGetResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DeletionStatusGetResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = DeletionStatusGetResponse()
        if mapping_value and mapping_value.casefold() == "CollectionDeletedResponse".casefold():
            from .....models.collection_deleted_response import CollectionDeletedResponse

            result.collection_deleted_response = CollectionDeletedResponse()
        elif mapping_value and mapping_value.casefold() == "CollectionPendingResponse".casefold():
            from .....models.collection_pending_response import CollectionPendingResponse

            result.collection_pending_response = CollectionPendingResponse()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .....models.collection_deleted_response import CollectionDeletedResponse
        from .....models.collection_pending_response import CollectionPendingResponse

        if self.collection_deleted_response:
            return self.collection_deleted_response.get_field_deserializers()
        if self.collection_pending_response:
            return self.collection_pending_response.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.collection_deleted_response:
            writer.write_object_value(None, self.collection_deleted_response)
        elif self.collection_pending_response:
            writer.write_object_value(None, self.collection_pending_response)
    

