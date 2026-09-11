from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .vector_key_value_list_pair import VectorKeyValueListPair
    from .vector_search_configuration import VectorSearchConfiguration
    from .vector_search_document_key_value_list_pair import VectorSearchDocumentKeyValueListPair
    from .vector_search_filter_filter import VectorSearchFilter_filter

@dataclass
class VectorSearchFilter(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Restrict chunks considered during search to those with the given metadata.
    chunk_metadata: Optional[list[VectorKeyValueListPair]] = None
    # The collectionIds property
    collection_ids: Optional[list[str]] = None
    # Restrict collections considered during search to those annotated with the given metadata. Useful when combined with collections=['*']
    collection_metadata: Optional[list[VectorKeyValueListPair]] = None
    # The configuration property
    configuration: Optional[VectorSearchConfiguration] = None
    # Restrict documents considered during search to those annotated with the given metadata.
    document_metadata: Optional[list[VectorSearchDocumentKeyValueListPair]] = None
    # Advanced filter expression for combining metadata filters with boolean logic
    filter: Optional[VectorSearchFilter_filter] = None
    # Identifier of this VectorSearchFilter - unique per request.
    id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VectorSearchFilter:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VectorSearchFilter
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VectorSearchFilter()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .vector_key_value_list_pair import VectorKeyValueListPair
        from .vector_search_configuration import VectorSearchConfiguration
        from .vector_search_document_key_value_list_pair import VectorSearchDocumentKeyValueListPair
        from .vector_search_filter_filter import VectorSearchFilter_filter

        from .vector_key_value_list_pair import VectorKeyValueListPair
        from .vector_search_configuration import VectorSearchConfiguration
        from .vector_search_document_key_value_list_pair import VectorSearchDocumentKeyValueListPair
        from .vector_search_filter_filter import VectorSearchFilter_filter

        fields: dict[str, Callable[[Any], None]] = {
            "chunkMetadata": lambda n : setattr(self, 'chunk_metadata', n.get_collection_of_object_values(VectorKeyValueListPair)),
            "collectionIds": lambda n : setattr(self, 'collection_ids', n.get_collection_of_primitive_values(str)),
            "collectionMetadata": lambda n : setattr(self, 'collection_metadata', n.get_collection_of_object_values(VectorKeyValueListPair)),
            "configuration": lambda n : setattr(self, 'configuration', n.get_object_value(VectorSearchConfiguration)),
            "documentMetadata": lambda n : setattr(self, 'document_metadata', n.get_collection_of_object_values(VectorSearchDocumentKeyValueListPair)),
            "filter": lambda n : setattr(self, 'filter', n.get_object_value(VectorSearchFilter_filter)),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
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
        writer.write_collection_of_primitive_values("collectionIds", self.collection_ids)
        writer.write_collection_of_object_values("collectionMetadata", self.collection_metadata)
        writer.write_object_value("configuration", self.configuration)
        writer.write_collection_of_object_values("documentMetadata", self.document_metadata)
        writer.write_object_value("filter", self.filter)
        writer.write_str_value("id", self.id)
        writer.write_additional_data_value(self.additional_data)
    

