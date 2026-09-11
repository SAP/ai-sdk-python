from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .merge_strategy_reranker_boosting import MergeStrategyReranker_boosting
    from .merge_strategy_reranker_model import MergeStrategyReranker_model
    from .merge_strategy_type import MergeStrategyType

@dataclass
class MergeStrategyReranker(AdditionalDataHolder, Parsable):
    """
    The MergeStrategyReranker will call a reranker LLM to merge the given PerFilterSearchResult instances. This strategy adds latency, but yields good results.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # If true, document and chunk metadata are sent to the reranker LLM along with the text content of the chunk.
    include_all_meta_data: Optional[bool] = False
    from .merge_strategy_reranker_model import MergeStrategyReranker_model

    # The RerankerModel to use.
    model: Optional[MergeStrategyReranker_model] = MergeStrategyReranker_model("cohere-3.5")
    # Key-value pairs to be included in the ranking process, to boost related chunks according to chunk content and metadata, if includeMetaData is true.
    boosting: Optional[list[MergeStrategyReranker_boosting]] = None
    # The type property
    type: Optional[MergeStrategyType] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MergeStrategyReranker:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MergeStrategyReranker
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MergeStrategyReranker()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .merge_strategy_reranker_boosting import MergeStrategyReranker_boosting
        from .merge_strategy_reranker_model import MergeStrategyReranker_model
        from .merge_strategy_type import MergeStrategyType

        from .merge_strategy_reranker_boosting import MergeStrategyReranker_boosting
        from .merge_strategy_reranker_model import MergeStrategyReranker_model
        from .merge_strategy_type import MergeStrategyType

        fields: dict[str, Callable[[Any], None]] = {
            "boosting": lambda n : setattr(self, 'boosting', n.get_collection_of_object_values(MergeStrategyReranker_boosting)),
            "includeAllMetaData": lambda n : setattr(self, 'include_all_meta_data', n.get_bool_value()),
            "model": lambda n : setattr(self, 'model', n.get_enum_value(MergeStrategyReranker_model)),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(MergeStrategyType)),
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
        writer.write_collection_of_object_values("boosting", self.boosting)
        writer.write_bool_value("includeAllMetaData", self.include_all_meta_data)
        writer.write_enum_value("model", self.model)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

