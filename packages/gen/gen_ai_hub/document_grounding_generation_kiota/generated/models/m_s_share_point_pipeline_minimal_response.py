from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .base_pipeline_minimal_response import BasePipelineMinimalResponse
    from .m_s_share_point_configuration_minimal import MSSharePointConfigurationMinimal
    from .m_s_share_point_pipeline_minimal_response_type import MSSharePointPipelineMinimalResponse_type

from .base_pipeline_minimal_response import BasePipelineMinimalResponse

@dataclass
class MSSharePointPipelineMinimalResponse(BasePipelineMinimalResponse, Parsable):
    # The configuration property
    configuration: Optional[MSSharePointConfigurationMinimal] = None
    # The metadata property
    metadata: Optional[bool] = None
    # The type property
    type: Optional[MSSharePointPipelineMinimalResponse_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MSSharePointPipelineMinimalResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MSSharePointPipelineMinimalResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MSSharePointPipelineMinimalResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .base_pipeline_minimal_response import BasePipelineMinimalResponse
        from .m_s_share_point_configuration_minimal import MSSharePointConfigurationMinimal
        from .m_s_share_point_pipeline_minimal_response_type import MSSharePointPipelineMinimalResponse_type

        from .base_pipeline_minimal_response import BasePipelineMinimalResponse
        from .m_s_share_point_configuration_minimal import MSSharePointConfigurationMinimal
        from .m_s_share_point_pipeline_minimal_response_type import MSSharePointPipelineMinimalResponse_type

        fields: dict[str, Callable[[Any], None]] = {
            "configuration": lambda n : setattr(self, 'configuration', n.get_object_value(MSSharePointConfigurationMinimal)),
            "metadata": lambda n : setattr(self, 'metadata', n.get_bool_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(MSSharePointPipelineMinimalResponse_type)),
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
    

