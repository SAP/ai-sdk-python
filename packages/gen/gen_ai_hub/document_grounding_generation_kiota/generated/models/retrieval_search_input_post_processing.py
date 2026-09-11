from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieval_search_input_post_processing_inputs import RetrievalSearchInput_postProcessing_inputs
    from .retrieval_search_input_post_processing_strategy import RetrievalSearchInput_postProcessing_strategy

@dataclass
class RetrievalSearchInput_postProcessing(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # New ID for each PostProcessingOperation.
    id: Optional[str] = "ae9eee48-4671-4321-a3e5-640adaaf26ae"
    # Maximum number of chunks to be retained in final PerSearchFilterResult.
    max_chunk_count: Optional[int] = 5
    # The inputs property
    inputs: Optional[list[RetrievalSearchInput_postProcessing_inputs]] = None
    # Merging and scoring strategy to derive final PerSearchFilterResult.
    strategy: Optional[RetrievalSearchInput_postProcessing_strategy] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalSearchInput_postProcessing:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalSearchInput_postProcessing
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrievalSearchInput_postProcessing()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieval_search_input_post_processing_inputs import RetrievalSearchInput_postProcessing_inputs
        from .retrieval_search_input_post_processing_strategy import RetrievalSearchInput_postProcessing_strategy

        from .retrieval_search_input_post_processing_inputs import RetrievalSearchInput_postProcessing_inputs
        from .retrieval_search_input_post_processing_strategy import RetrievalSearchInput_postProcessing_strategy

        fields: dict[str, Callable[[Any], None]] = {
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "inputs": lambda n : setattr(self, 'inputs', n.get_collection_of_object_values(RetrievalSearchInput_postProcessing_inputs)),
            "maxChunkCount": lambda n : setattr(self, 'max_chunk_count', n.get_int_value()),
            "strategy": lambda n : setattr(self, 'strategy', n.get_object_value(RetrievalSearchInput_postProcessing_strategy)),
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
        writer.write_str_value("id", self.id)
        writer.write_collection_of_object_values("inputs", self.inputs)
        writer.write_int_value("maxChunkCount", self.max_chunk_count)
        writer.write_object_value("strategy", self.strategy)
        writer.write_additional_data_value(self.additional_data)
    

