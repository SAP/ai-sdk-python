from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieval_key_value_list_pair import RetrievalKeyValueListPair
    from .score import Score
    from .search_scores import SearchScores

@dataclass
class RetrievalChunk(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The content property
    content: Optional[str] = None
    # The id property
    id: Optional[str] = None
    # The metadata property
    metadata: Optional[list[RetrievalKeyValueListPair]] = None
    # The postProcessingScore property
    post_processing_score: Optional[Score] = None
    # The searchScores property
    search_scores: Optional[SearchScores] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalChunk:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalChunk
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrievalChunk()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieval_key_value_list_pair import RetrievalKeyValueListPair
        from .score import Score
        from .search_scores import SearchScores

        from .retrieval_key_value_list_pair import RetrievalKeyValueListPair
        from .score import Score
        from .search_scores import SearchScores

        fields: dict[str, Callable[[Any], None]] = {
            "content": lambda n : setattr(self, 'content', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "metadata": lambda n : setattr(self, 'metadata', n.get_collection_of_object_values(RetrievalKeyValueListPair)),
            "postProcessingScore": lambda n : setattr(self, 'post_processing_score', n.get_object_value(Score)),
            "searchScores": lambda n : setattr(self, 'search_scores', n.get_object_value(SearchScores)),
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
        writer.write_str_value("content", self.content)
        writer.write_str_value("id", self.id)
        writer.write_collection_of_object_values("metadata", self.metadata)
        writer.write_object_value("postProcessingScore", self.post_processing_score)
        writer.write_object_value("searchScores", self.search_scores)
        writer.write_additional_data_value(self.additional_data)
    

