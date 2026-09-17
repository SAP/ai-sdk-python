from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .embedding_config import EmbeddingConfig
    from .vector_key_value_list_pair import VectorKeyValueListPair

@dataclass
class Collection(AdditionalDataHolder, Parsable):
    """
    A logical grouping of content.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The embeddingConfig property
    embedding_config: Optional[EmbeddingConfig] = None
    # Unique identifier of a collection.
    id: Optional[UUID] = None
    # Metadata attached to collection. Useful to restrict search to a subset of collections.
    metadata: Optional[list[VectorKeyValueListPair]] = None
    # The title property
    title: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Collection:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Collection
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Collection()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .embedding_config import EmbeddingConfig
        from .vector_key_value_list_pair import VectorKeyValueListPair

        from .embedding_config import EmbeddingConfig
        from .vector_key_value_list_pair import VectorKeyValueListPair

        fields: dict[str, Callable[[Any], None]] = {
            "embeddingConfig": lambda n : setattr(self, 'embedding_config', n.get_object_value(EmbeddingConfig)),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "metadata": lambda n : setattr(self, 'metadata', n.get_collection_of_object_values(VectorKeyValueListPair)),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
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
        writer.write_object_value("embeddingConfig", self.embedding_config)
        writer.write_uuid_value("id", self.id)
        writer.write_collection_of_object_values("metadata", self.metadata)
        writer.write_str_value("title", self.title)
        writer.write_additional_data_value(self.additional_data)
    

