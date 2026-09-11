from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .search_scores_aggregated_score import SearchScores_aggregatedScore
    from .search_scores_dense_retrieval_score import SearchScores_denseRetrievalScore

@dataclass
class SearchScores(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The aggregatedScore property
    aggregated_score: Optional[SearchScores_aggregatedScore] = None
    # The denseRetrievalScore property
    dense_retrieval_score: Optional[SearchScores_denseRetrievalScore] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SearchScores:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SearchScores
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SearchScores()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .search_scores_aggregated_score import SearchScores_aggregatedScore
        from .search_scores_dense_retrieval_score import SearchScores_denseRetrievalScore

        from .search_scores_aggregated_score import SearchScores_aggregatedScore
        from .search_scores_dense_retrieval_score import SearchScores_denseRetrievalScore

        fields: dict[str, Callable[[Any], None]] = {
            "aggregatedScore": lambda n : setattr(self, 'aggregated_score', n.get_object_value(SearchScores_aggregatedScore)),
            "denseRetrievalScore": lambda n : setattr(self, 'dense_retrieval_score', n.get_object_value(SearchScores_denseRetrievalScore)),
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
        writer.write_object_value("aggregatedScore", self.aggregated_score)
        writer.write_object_value("denseRetrievalScore", self.dense_retrieval_score)
        writer.write_additional_data_value(self.additional_data)
    

