from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .document import Document
    from .retrieval_key_value_list_pair import RetrievalKeyValueListPair

@dataclass
class DataRepositoryWithDocuments(AdditionalDataHolder, Parsable):
    """
    DataRepository schema returned by the Vector search endpoint
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The documents property
    documents: Optional[list[Document]] = None
    # Unique identifier of this DataRepository.
    id: Optional[UUID] = None
    # Optional message.
    message: Optional[str] = None
    # Metadata attached to DataRepository. Useful to later limit search to a subset of DataRepositories.
    metadata: Optional[list[RetrievalKeyValueListPair]] = None
    # Friendly destination Name (grounding.name) of remote instance.
    remote_grounding_name: Optional[str] = None
    # The title property
    title: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DataRepositoryWithDocuments:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DataRepositoryWithDocuments
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DataRepositoryWithDocuments()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .document import Document
        from .retrieval_key_value_list_pair import RetrievalKeyValueListPair

        from .document import Document
        from .retrieval_key_value_list_pair import RetrievalKeyValueListPair

        fields: dict[str, Callable[[Any], None]] = {
            "documents": lambda n : setattr(self, 'documents', n.get_collection_of_object_values(Document)),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
            "metadata": lambda n : setattr(self, 'metadata', n.get_collection_of_object_values(RetrievalKeyValueListPair)),
            "remoteGroundingName": lambda n : setattr(self, 'remote_grounding_name', n.get_str_value()),
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
        writer.write_collection_of_object_values("documents", self.documents)
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("message", self.message)
        writer.write_collection_of_object_values("metadata", self.metadata)
        writer.write_str_value("remoteGroundingName", self.remote_grounding_name)
        writer.write_str_value("title", self.title)
        writer.write_additional_data_value(self.additional_data)
    

