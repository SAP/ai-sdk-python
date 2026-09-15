from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .search_pipeline_data_repository_metadata import SearchPipeline_dataRepositoryMetadata

@dataclass
class SearchPipeline(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Search for metadata happens at key level. Pipelines matching the search criteria will be returned.
    data_repository_metadata: Optional[list[SearchPipeline_dataRepositoryMetadata]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SearchPipeline:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SearchPipeline
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SearchPipeline()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .search_pipeline_data_repository_metadata import SearchPipeline_dataRepositoryMetadata

        from .search_pipeline_data_repository_metadata import SearchPipeline_dataRepositoryMetadata

        fields: dict[str, Callable[[Any], None]] = {
            "dataRepositoryMetadata": lambda n : setattr(self, 'data_repository_metadata', n.get_collection_of_object_values(SearchPipeline_dataRepositoryMetadata)),
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
        writer.write_collection_of_object_values("dataRepositoryMetadata", self.data_repository_metadata)
        writer.write_additional_data_value(self.additional_data)
    

