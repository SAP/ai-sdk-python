from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .data_repository_with_documents import DataRepositoryWithDocuments

@dataclass
class RetrievalDataRepositorySearchResult(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # DataRepository schema returned by the Vector search endpoint
    data_repository: Optional[DataRepositoryWithDocuments] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalDataRepositorySearchResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalDataRepositorySearchResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrievalDataRepositorySearchResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .data_repository_with_documents import DataRepositoryWithDocuments

        from .data_repository_with_documents import DataRepositoryWithDocuments

        fields: dict[str, Callable[[Any], None]] = {
            "dataRepository": lambda n : setattr(self, 'data_repository', n.get_object_value(DataRepositoryWithDocuments)),
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
        writer.write_object_value("dataRepository", self.data_repository)
        writer.write_additional_data_value(self.additional_data)
    

