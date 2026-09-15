from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .metadata_key_update import MetadataKeyUpdate

@dataclass
class MetadataUpdateItem(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # List of collection or document or chunk ids for which the metadata should be updated
    ids: Optional[list[UUID]] = None
    # List of metadata updates for the given resource ids
    metadata_updates: Optional[list[MetadataKeyUpdate]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MetadataUpdateItem:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MetadataUpdateItem
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MetadataUpdateItem()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .metadata_key_update import MetadataKeyUpdate

        from .metadata_key_update import MetadataKeyUpdate

        fields: dict[str, Callable[[Any], None]] = {
            "ids": lambda n : setattr(self, 'ids', n.get_collection_of_primitive_values(UUID)),
            "metadataUpdates": lambda n : setattr(self, 'metadata_updates', n.get_collection_of_object_values(MetadataKeyUpdate)),
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
        writer.write_collection_of_primitive_values("ids", self.ids)
        writer.write_collection_of_object_values("metadataUpdates", self.metadata_updates)
        writer.write_additional_data_value(self.additional_data)
    

