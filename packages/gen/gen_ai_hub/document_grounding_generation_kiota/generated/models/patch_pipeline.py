from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .patch_pipeline_configuration import PatchPipeline_configuration
    from .patch_pipeline_metadata import PatchPipeline_metadata

@dataclass
class PatchPipeline(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The configuration property
    configuration: Optional[PatchPipeline_configuration] = None
    # The metadata property
    metadata: Optional[PatchPipeline_metadata] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PatchPipeline:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PatchPipeline
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PatchPipeline()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .patch_pipeline_configuration import PatchPipeline_configuration
        from .patch_pipeline_metadata import PatchPipeline_metadata

        from .patch_pipeline_configuration import PatchPipeline_configuration
        from .patch_pipeline_metadata import PatchPipeline_metadata

        fields: dict[str, Callable[[Any], None]] = {
            "configuration": lambda n : setattr(self, 'configuration', n.get_object_value(PatchPipeline_configuration)),
            "metadata": lambda n : setattr(self, 'metadata', n.get_object_value(PatchPipeline_metadata)),
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
        writer.write_object_value("configuration", self.configuration)
        writer.write_object_value("metadata", self.metadata)
        writer.write_additional_data_value(self.additional_data)
    

