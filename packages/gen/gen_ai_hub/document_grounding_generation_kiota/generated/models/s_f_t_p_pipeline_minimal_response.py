from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .base_pipeline_minimal_response import BasePipelineMinimalResponse
    from .s_f_t_p_configuration_minimal import SFTPConfigurationMinimal
    from .s_f_t_p_pipeline_minimal_response_type import SFTPPipelineMinimalResponse_type

from .base_pipeline_minimal_response import BasePipelineMinimalResponse

@dataclass
class SFTPPipelineMinimalResponse(BasePipelineMinimalResponse, Parsable):
    # The configuration property
    configuration: Optional[SFTPConfigurationMinimal] = None
    # The metadata property
    metadata: Optional[bool] = None
    # The type property
    type: Optional[SFTPPipelineMinimalResponse_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SFTPPipelineMinimalResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SFTPPipelineMinimalResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SFTPPipelineMinimalResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .base_pipeline_minimal_response import BasePipelineMinimalResponse
        from .s_f_t_p_configuration_minimal import SFTPConfigurationMinimal
        from .s_f_t_p_pipeline_minimal_response_type import SFTPPipelineMinimalResponse_type

        from .base_pipeline_minimal_response import BasePipelineMinimalResponse
        from .s_f_t_p_configuration_minimal import SFTPConfigurationMinimal
        from .s_f_t_p_pipeline_minimal_response_type import SFTPPipelineMinimalResponse_type

        fields: dict[str, Callable[[Any], None]] = {
            "configuration": lambda n : setattr(self, 'configuration', n.get_object_value(SFTPConfigurationMinimal)),
            "metadata": lambda n : setattr(self, 'metadata', n.get_bool_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(SFTPPipelineMinimalResponse_type)),
        }
        super_fields = super().get_field_deserializers()
        fields.update(super_fields)
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        super().serialize(writer)
        writer.write_object_value("configuration", self.configuration)
        writer.write_bool_value("metadata", self.metadata)
        writer.write_enum_value("type", self.type)
    

