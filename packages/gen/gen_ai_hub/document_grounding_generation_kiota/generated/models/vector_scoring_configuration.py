from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .boosting_scoring_configuration import BoostingScoringConfiguration
    from .dense_retrieval_scoring_configuration import DenseRetrievalScoringConfiguration
    from .key_word_retrieval_scoring_configuration import KeyWordRetrievalScoringConfiguration
    from .scores_aggregation_strategy import ScoresAggregationStrategy

@dataclass
class VectorScoringConfiguration(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The aggregationStrategy property
    aggregation_strategy: Optional[ScoresAggregationStrategy] = None
    # The boosting property
    boosting: Optional[BoostingScoringConfiguration] = None
    # The denseRetrieval property
    dense_retrieval: Optional[DenseRetrievalScoringConfiguration] = None
    # The keywordRetrieval property
    keyword_retrieval: Optional[KeyWordRetrievalScoringConfiguration] = None
    # Minimum chunk score threshold.
    score_threshold: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VectorScoringConfiguration:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VectorScoringConfiguration
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VectorScoringConfiguration()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .boosting_scoring_configuration import BoostingScoringConfiguration
        from .dense_retrieval_scoring_configuration import DenseRetrievalScoringConfiguration
        from .key_word_retrieval_scoring_configuration import KeyWordRetrievalScoringConfiguration
        from .scores_aggregation_strategy import ScoresAggregationStrategy

        from .boosting_scoring_configuration import BoostingScoringConfiguration
        from .dense_retrieval_scoring_configuration import DenseRetrievalScoringConfiguration
        from .key_word_retrieval_scoring_configuration import KeyWordRetrievalScoringConfiguration
        from .scores_aggregation_strategy import ScoresAggregationStrategy

        fields: dict[str, Callable[[Any], None]] = {
            "aggregationStrategy": lambda n : setattr(self, 'aggregation_strategy', n.get_enum_value(ScoresAggregationStrategy)),
            "boosting": lambda n : setattr(self, 'boosting', n.get_object_value(BoostingScoringConfiguration)),
            "denseRetrieval": lambda n : setattr(self, 'dense_retrieval', n.get_object_value(DenseRetrievalScoringConfiguration)),
            "keywordRetrieval": lambda n : setattr(self, 'keyword_retrieval', n.get_object_value(KeyWordRetrievalScoringConfiguration)),
            "scoreThreshold": lambda n : setattr(self, 'score_threshold', n.get_float_value()),
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
        writer.write_enum_value("aggregationStrategy", self.aggregation_strategy)
        writer.write_object_value("boosting", self.boosting)
        writer.write_object_value("denseRetrieval", self.dense_retrieval)
        writer.write_object_value("keywordRetrieval", self.keyword_retrieval)
        writer.write_float_value("scoreThreshold", self.score_threshold)
        writer.write_additional_data_value(self.additional_data)
    

