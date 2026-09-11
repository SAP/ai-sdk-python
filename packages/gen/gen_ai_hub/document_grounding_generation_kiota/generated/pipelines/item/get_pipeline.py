from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ...models.google_drive_pipeline_get_response import GoogleDrivePipelineGetResponse
    from ...models.m_s_share_point_pipeline_get_response import MSSharePointPipelineGetResponse
    from ...models.s3_pipeline_get_response import S3PipelineGetResponse
    from ...models.service_now_pipeline_get_response import ServiceNowPipelineGetResponse
    from ...models.s_d_m_pipeline_get_response import SDMPipelineGetResponse
    from ...models.s_f_t_p_pipeline_get_response import SFTPPipelineGetResponse
    from ...models.work_zone_pipeline_get_response import WorkZonePipelineGetResponse

@dataclass
class GetPipeline(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes GoogleDrivePipelineGetResponse, MSSharePointPipelineGetResponse, S3PipelineGetResponse, SDMPipelineGetResponse, ServiceNowPipelineGetResponse, SFTPPipelineGetResponse, WorkZonePipelineGetResponse
    """
    # Composed type representation for type GoogleDrivePipelineGetResponse
    google_drive_pipeline_get_response: Optional[GoogleDrivePipelineGetResponse] = None
    # Composed type representation for type MSSharePointPipelineGetResponse
    m_s_share_point_pipeline_get_response: Optional[MSSharePointPipelineGetResponse] = None
    # Composed type representation for type SDMPipelineGetResponse
    s_d_m_pipeline_get_response: Optional[SDMPipelineGetResponse] = None
    # Composed type representation for type SFTPPipelineGetResponse
    s_f_t_p_pipeline_get_response: Optional[SFTPPipelineGetResponse] = None
    # Composed type representation for type S3PipelineGetResponse
    s3_pipeline_get_response: Optional[S3PipelineGetResponse] = None
    # Composed type representation for type ServiceNowPipelineGetResponse
    service_now_pipeline_get_response: Optional[ServiceNowPipelineGetResponse] = None
    # Composed type representation for type WorkZonePipelineGetResponse
    work_zone_pipeline_get_response: Optional[WorkZonePipelineGetResponse] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetPipeline:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetPipeline
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("type")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = GetPipeline()
        if mapping_value and mapping_value.casefold() == "GoogleDrive".casefold():
            from ...models.google_drive_pipeline_get_response import GoogleDrivePipelineGetResponse

            result.google_drive_pipeline_get_response = GoogleDrivePipelineGetResponse()
        elif mapping_value and mapping_value.casefold() == "MSSharePoint".casefold():
            from ...models.m_s_share_point_pipeline_get_response import MSSharePointPipelineGetResponse

            result.m_s_share_point_pipeline_get_response = MSSharePointPipelineGetResponse()
        elif mapping_value and mapping_value.casefold() == "SDM".casefold():
            from ...models.s_d_m_pipeline_get_response import SDMPipelineGetResponse

            result.s_d_m_pipeline_get_response = SDMPipelineGetResponse()
        elif mapping_value and mapping_value.casefold() == "SFTP".casefold():
            from ...models.s_f_t_p_pipeline_get_response import SFTPPipelineGetResponse

            result.s_f_t_p_pipeline_get_response = SFTPPipelineGetResponse()
        elif mapping_value and mapping_value.casefold() == "S3".casefold():
            from ...models.s3_pipeline_get_response import S3PipelineGetResponse

            result.s3_pipeline_get_response = S3PipelineGetResponse()
        elif mapping_value and mapping_value.casefold() == "ServiceNow".casefold():
            from ...models.service_now_pipeline_get_response import ServiceNowPipelineGetResponse

            result.service_now_pipeline_get_response = ServiceNowPipelineGetResponse()
        elif mapping_value and mapping_value.casefold() == "WorkZone".casefold():
            from ...models.work_zone_pipeline_get_response import WorkZonePipelineGetResponse

            result.work_zone_pipeline_get_response = WorkZonePipelineGetResponse()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from ...models.google_drive_pipeline_get_response import GoogleDrivePipelineGetResponse
        from ...models.m_s_share_point_pipeline_get_response import MSSharePointPipelineGetResponse
        from ...models.s3_pipeline_get_response import S3PipelineGetResponse
        from ...models.service_now_pipeline_get_response import ServiceNowPipelineGetResponse
        from ...models.s_d_m_pipeline_get_response import SDMPipelineGetResponse
        from ...models.s_f_t_p_pipeline_get_response import SFTPPipelineGetResponse
        from ...models.work_zone_pipeline_get_response import WorkZonePipelineGetResponse

        if self.google_drive_pipeline_get_response:
            return self.google_drive_pipeline_get_response.get_field_deserializers()
        if self.m_s_share_point_pipeline_get_response:
            return self.m_s_share_point_pipeline_get_response.get_field_deserializers()
        if self.s_d_m_pipeline_get_response:
            return self.s_d_m_pipeline_get_response.get_field_deserializers()
        if self.s_f_t_p_pipeline_get_response:
            return self.s_f_t_p_pipeline_get_response.get_field_deserializers()
        if self.s3_pipeline_get_response:
            return self.s3_pipeline_get_response.get_field_deserializers()
        if self.service_now_pipeline_get_response:
            return self.service_now_pipeline_get_response.get_field_deserializers()
        if self.work_zone_pipeline_get_response:
            return self.work_zone_pipeline_get_response.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.google_drive_pipeline_get_response:
            writer.write_object_value(None, self.google_drive_pipeline_get_response)
        elif self.m_s_share_point_pipeline_get_response:
            writer.write_object_value(None, self.m_s_share_point_pipeline_get_response)
        elif self.s_d_m_pipeline_get_response:
            writer.write_object_value(None, self.s_d_m_pipeline_get_response)
        elif self.s_f_t_p_pipeline_get_response:
            writer.write_object_value(None, self.s_f_t_p_pipeline_get_response)
        elif self.s3_pipeline_get_response:
            writer.write_object_value(None, self.s3_pipeline_get_response)
        elif self.service_now_pipeline_get_response:
            writer.write_object_value(None, self.service_now_pipeline_get_response)
        elif self.work_zone_pipeline_get_response:
            writer.write_object_value(None, self.work_zone_pipeline_get_response)
    

