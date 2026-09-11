from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .pipeline_execution_data import PipelineExecutionData

@dataclass
class GetPipelineExecutions(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The count property
    count: Optional[int] = None
    # The resources property
    resources: Optional[list[PipelineExecutionData]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetPipelineExecutions:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetPipelineExecutions
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetPipelineExecutions()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .pipeline_execution_data import PipelineExecutionData

        from .pipeline_execution_data import PipelineExecutionData

        fields: dict[str, Callable[[Any], None]] = {
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
            "resources": lambda n : setattr(self, 'resources', n.get_collection_of_object_values(PipelineExecutionData)),
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
        writer.write_int_value("count", self.count)
        writer.write_collection_of_object_values("resources", self.resources)
        writer.write_additional_data_value(self.additional_data)
    

