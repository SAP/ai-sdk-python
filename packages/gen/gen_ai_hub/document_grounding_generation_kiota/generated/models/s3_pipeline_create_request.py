from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .meta_data import MetaData
    from .s3_configuration import S3Configuration
    from .s3_pipeline_create_request_type import S3PipelineCreateRequest_type

@dataclass
class S3PipelineCreateRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The configuration property
    configuration: Optional[S3Configuration] = None
    # The metadata property
    metadata: Optional[MetaData] = None
    # The type property
    type: Optional[S3PipelineCreateRequest_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> S3PipelineCreateRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: S3PipelineCreateRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return S3PipelineCreateRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .meta_data import MetaData
        from .s3_configuration import S3Configuration
        from .s3_pipeline_create_request_type import S3PipelineCreateRequest_type

        from .meta_data import MetaData
        from .s3_configuration import S3Configuration
        from .s3_pipeline_create_request_type import S3PipelineCreateRequest_type

        fields: dict[str, Callable[[Any], None]] = {
            "configuration": lambda n : setattr(self, 'configuration', n.get_object_value(S3Configuration)),
            "metadata": lambda n : setattr(self, 'metadata', n.get_object_value(MetaData)),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(S3PipelineCreateRequest_type)),
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
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

