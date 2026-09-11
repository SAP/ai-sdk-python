from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .data_repository_type import DataRepositoryType
    from .retrieval_key_value_list_pair import RetrievalKeyValueListPair
    from .retrieval_search_configuration import RetrievalSearchConfiguration
    from .retrieval_search_document_key_value_list_pair import RetrievalSearchDocumentKeyValueListPair

@dataclass
class RetrievalSearchFilter(AdditionalDataHolder, Parsable):
    """
    Limit scope of search to certain DataRepositories, Documents or Chunks.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Restrict chunks considered during search to those with the given metadata.
    chunk_metadata: Optional[list[RetrievalKeyValueListPair]] = None
    # Specify ['*'] to search across all DataRepositories or give a specific list of DataRepository ids.
    data_repositories: Optional[list[str]] = None
    # Restrict DataRepositories considered during search to those annotated with the given metadata. Useful when combined with dataRepositories=['*']
    data_repository_metadata: Optional[list[RetrievalKeyValueListPair]] = None
    # Only include DataRepositories with the given type.
    data_repository_type: Optional[DataRepositoryType] = None
    # Restrict documents considered during search to those annotated with the given metadata.
    document_metadata: Optional[list[RetrievalSearchDocumentKeyValueListPair]] = None
    # Identifier of this RetrievalSearchFilter - unique per request.
    id: Optional[str] = None
    # Destination Name of remote instance.
    remote_name: Optional[str] = None
    # The searchConfiguration property
    search_configuration: Optional[RetrievalSearchConfiguration] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalSearchFilter:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalSearchFilter
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrievalSearchFilter()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .data_repository_type import DataRepositoryType
        from .retrieval_key_value_list_pair import RetrievalKeyValueListPair
        from .retrieval_search_configuration import RetrievalSearchConfiguration
        from .retrieval_search_document_key_value_list_pair import RetrievalSearchDocumentKeyValueListPair

        from .data_repository_type import DataRepositoryType
        from .retrieval_key_value_list_pair import RetrievalKeyValueListPair
        from .retrieval_search_configuration import RetrievalSearchConfiguration
        from .retrieval_search_document_key_value_list_pair import RetrievalSearchDocumentKeyValueListPair

        fields: dict[str, Callable[[Any], None]] = {
            "chunkMetadata": lambda n : setattr(self, 'chunk_metadata', n.get_collection_of_object_values(RetrievalKeyValueListPair)),
            "dataRepositories": lambda n : setattr(self, 'data_repositories', n.get_collection_of_primitive_values(str)),
            "dataRepositoryMetadata": lambda n : setattr(self, 'data_repository_metadata', n.get_collection_of_object_values(RetrievalKeyValueListPair)),
            "dataRepositoryType": lambda n : setattr(self, 'data_repository_type', n.get_enum_value(DataRepositoryType)),
            "documentMetadata": lambda n : setattr(self, 'document_metadata', n.get_collection_of_object_values(RetrievalSearchDocumentKeyValueListPair)),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "remoteName": lambda n : setattr(self, 'remote_name', n.get_str_value()),
            "searchConfiguration": lambda n : setattr(self, 'search_configuration', n.get_object_value(RetrievalSearchConfiguration)),
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
        writer.write_collection_of_object_values("chunkMetadata", self.chunk_metadata)
        writer.write_collection_of_primitive_values("dataRepositories", self.data_repositories)
        writer.write_collection_of_object_values("dataRepositoryMetadata", self.data_repository_metadata)
        writer.write_enum_value("dataRepositoryType", self.data_repository_type)
        writer.write_collection_of_object_values("documentMetadata", self.document_metadata)
        writer.write_str_value("id", self.id)
        writer.write_str_value("remoteName", self.remote_name)
        writer.write_object_value("searchConfiguration", self.search_configuration)
        writer.write_additional_data_value(self.additional_data)
    

