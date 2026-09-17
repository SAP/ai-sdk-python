from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..models.google_drive_pipeline_create_request import GoogleDrivePipelineCreateRequest
    from ..models.metadata_configuration import MetadataConfiguration
    from ..models.m_s_share_point_pipeline_create_request import MSSharePointPipelineCreateRequest
    from ..models.s3_pipeline_create_request import S3PipelineCreateRequest
    from ..models.service_now_pipeline_create_request import ServiceNowPipelineCreateRequest
    from ..models.s_d_m_pipeline_create_request import SDMPipelineCreateRequest
    from ..models.s_f_t_p_pipeline_create_request import SFTPPipelineCreateRequest
    from ..models.work_zone_pipeline_create_request import WorkZonePipelineCreateRequest

@dataclass
class CreatePipeline(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes GoogleDrivePipelineCreateRequest, MetadataConfiguration, MSSharePointPipelineCreateRequest, S3PipelineCreateRequest, SDMPipelineCreateRequest, ServiceNowPipelineCreateRequest, SFTPPipelineCreateRequest, WorkZonePipelineCreateRequest
    """
    # Composed type representation for type GoogleDrivePipelineCreateRequest
    google_drive_pipeline_create_request: Optional[GoogleDrivePipelineCreateRequest] = None
    # Composed type representation for type MSSharePointPipelineCreateRequest
    m_s_share_point_pipeline_create_request: Optional[MSSharePointPipelineCreateRequest] = None
    # Composed type representation for type MetadataConfiguration
    metadata_configuration: Optional[MetadataConfiguration] = None
    # Composed type representation for type SDMPipelineCreateRequest
    s_d_m_pipeline_create_request: Optional[SDMPipelineCreateRequest] = None
    # Composed type representation for type SFTPPipelineCreateRequest
    s_f_t_p_pipeline_create_request: Optional[SFTPPipelineCreateRequest] = None
    # Composed type representation for type S3PipelineCreateRequest
    s3_pipeline_create_request: Optional[S3PipelineCreateRequest] = None
    # Composed type representation for type ServiceNowPipelineCreateRequest
    service_now_pipeline_create_request: Optional[ServiceNowPipelineCreateRequest] = None
    # Composed type representation for type WorkZonePipelineCreateRequest
    work_zone_pipeline_create_request: Optional[WorkZonePipelineCreateRequest] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CreatePipeline:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CreatePipeline
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("type")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = CreatePipeline()
        if mapping_value and mapping_value.casefold() == "GoogleDrive".casefold():
            from ..models.google_drive_pipeline_create_request import GoogleDrivePipelineCreateRequest

            result.google_drive_pipeline_create_request = GoogleDrivePipelineCreateRequest()
        elif mapping_value and mapping_value.casefold() == "MSSharePoint".casefold():
            from ..models.m_s_share_point_pipeline_create_request import MSSharePointPipelineCreateRequest

            result.m_s_share_point_pipeline_create_request = MSSharePointPipelineCreateRequest()
        elif mapping_value and mapping_value.casefold() == "metadata".casefold():
            from ..models.metadata_configuration import MetadataConfiguration

            result.metadata_configuration = MetadataConfiguration()
        elif mapping_value and mapping_value.casefold() == "SDM".casefold():
            from ..models.s_d_m_pipeline_create_request import SDMPipelineCreateRequest

            result.s_d_m_pipeline_create_request = SDMPipelineCreateRequest()
        elif mapping_value and mapping_value.casefold() == "SFTP".casefold():
            from ..models.s_f_t_p_pipeline_create_request import SFTPPipelineCreateRequest

            result.s_f_t_p_pipeline_create_request = SFTPPipelineCreateRequest()
        elif mapping_value and mapping_value.casefold() == "S3".casefold():
            from ..models.s3_pipeline_create_request import S3PipelineCreateRequest

            result.s3_pipeline_create_request = S3PipelineCreateRequest()
        elif mapping_value and mapping_value.casefold() == "ServiceNow".casefold():
            from ..models.service_now_pipeline_create_request import ServiceNowPipelineCreateRequest

            result.service_now_pipeline_create_request = ServiceNowPipelineCreateRequest()
        elif mapping_value and mapping_value.casefold() == "WorkZone".casefold():
            from ..models.work_zone_pipeline_create_request import WorkZonePipelineCreateRequest

            result.work_zone_pipeline_create_request = WorkZonePipelineCreateRequest()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from ..models.google_drive_pipeline_create_request import GoogleDrivePipelineCreateRequest
        from ..models.metadata_configuration import MetadataConfiguration
        from ..models.m_s_share_point_pipeline_create_request import MSSharePointPipelineCreateRequest
        from ..models.s3_pipeline_create_request import S3PipelineCreateRequest
        from ..models.service_now_pipeline_create_request import ServiceNowPipelineCreateRequest
        from ..models.s_d_m_pipeline_create_request import SDMPipelineCreateRequest
        from ..models.s_f_t_p_pipeline_create_request import SFTPPipelineCreateRequest
        from ..models.work_zone_pipeline_create_request import WorkZonePipelineCreateRequest

        if self.google_drive_pipeline_create_request:
            return self.google_drive_pipeline_create_request.get_field_deserializers()
        if self.m_s_share_point_pipeline_create_request:
            return self.m_s_share_point_pipeline_create_request.get_field_deserializers()
        if self.metadata_configuration:
            return self.metadata_configuration.get_field_deserializers()
        if self.s_d_m_pipeline_create_request:
            return self.s_d_m_pipeline_create_request.get_field_deserializers()
        if self.s_f_t_p_pipeline_create_request:
            return self.s_f_t_p_pipeline_create_request.get_field_deserializers()
        if self.s3_pipeline_create_request:
            return self.s3_pipeline_create_request.get_field_deserializers()
        if self.service_now_pipeline_create_request:
            return self.service_now_pipeline_create_request.get_field_deserializers()
        if self.work_zone_pipeline_create_request:
            return self.work_zone_pipeline_create_request.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.google_drive_pipeline_create_request:
            writer.write_object_value(None, self.google_drive_pipeline_create_request)
        elif self.m_s_share_point_pipeline_create_request:
            writer.write_object_value(None, self.m_s_share_point_pipeline_create_request)
        elif self.metadata_configuration:
            writer.write_object_value(None, self.metadata_configuration)
        elif self.s_d_m_pipeline_create_request:
            writer.write_object_value(None, self.s_d_m_pipeline_create_request)
        elif self.s_f_t_p_pipeline_create_request:
            writer.write_object_value(None, self.s_f_t_p_pipeline_create_request)
        elif self.s3_pipeline_create_request:
            writer.write_object_value(None, self.s3_pipeline_create_request)
        elif self.service_now_pipeline_create_request:
            writer.write_object_value(None, self.service_now_pipeline_create_request)
        elif self.work_zone_pipeline_create_request:
            writer.write_object_value(None, self.work_zone_pipeline_create_request)
    

