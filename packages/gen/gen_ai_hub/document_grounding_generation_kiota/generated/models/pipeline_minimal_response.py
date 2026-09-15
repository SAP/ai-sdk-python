from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .google_drive_pipeline_minimal_response import GoogleDrivePipelineMinimalResponse
    from .m_s_share_point_pipeline_minimal_response import MSSharePointPipelineMinimalResponse
    from .s3_pipeline_minimal_response import S3PipelineMinimalResponse
    from .service_now_pipeline_minimal_response import ServiceNowPipelineMinimalResponse
    from .s_d_m_pipeline_minimal_response import SDMPipelineMinimalResponse
    from .s_f_t_p_pipeline_minimal_response import SFTPPipelineMinimalResponse
    from .work_zone_pipeline_minimal_response import WorkZonePipelineMinimalResponse

@dataclass
class PipelineMinimalResponse(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes GoogleDrivePipelineMinimalResponse, MSSharePointPipelineMinimalResponse, S3PipelineMinimalResponse, SDMPipelineMinimalResponse, ServiceNowPipelineMinimalResponse, SFTPPipelineMinimalResponse, WorkZonePipelineMinimalResponse
    """
    # Composed type representation for type GoogleDrivePipelineMinimalResponse
    google_drive_pipeline_minimal_response: Optional[GoogleDrivePipelineMinimalResponse] = None
    # Composed type representation for type MSSharePointPipelineMinimalResponse
    m_s_share_point_pipeline_minimal_response: Optional[MSSharePointPipelineMinimalResponse] = None
    # Composed type representation for type SDMPipelineMinimalResponse
    s_d_m_pipeline_minimal_response: Optional[SDMPipelineMinimalResponse] = None
    # Composed type representation for type SFTPPipelineMinimalResponse
    s_f_t_p_pipeline_minimal_response: Optional[SFTPPipelineMinimalResponse] = None
    # Composed type representation for type S3PipelineMinimalResponse
    s3_pipeline_minimal_response: Optional[S3PipelineMinimalResponse] = None
    # Composed type representation for type ServiceNowPipelineMinimalResponse
    service_now_pipeline_minimal_response: Optional[ServiceNowPipelineMinimalResponse] = None
    # Composed type representation for type WorkZonePipelineMinimalResponse
    work_zone_pipeline_minimal_response: Optional[WorkZonePipelineMinimalResponse] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PipelineMinimalResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PipelineMinimalResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("type")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = PipelineMinimalResponse()
        if mapping_value and mapping_value.casefold() == "GoogleDrive".casefold():
            from .google_drive_pipeline_minimal_response import GoogleDrivePipelineMinimalResponse

            result.google_drive_pipeline_minimal_response = GoogleDrivePipelineMinimalResponse()
        elif mapping_value and mapping_value.casefold() == "MSSharePoint".casefold():
            from .m_s_share_point_pipeline_minimal_response import MSSharePointPipelineMinimalResponse

            result.m_s_share_point_pipeline_minimal_response = MSSharePointPipelineMinimalResponse()
        elif mapping_value and mapping_value.casefold() == "SDM".casefold():
            from .s_d_m_pipeline_minimal_response import SDMPipelineMinimalResponse

            result.s_d_m_pipeline_minimal_response = SDMPipelineMinimalResponse()
        elif mapping_value and mapping_value.casefold() == "SFTP".casefold():
            from .s_f_t_p_pipeline_minimal_response import SFTPPipelineMinimalResponse

            result.s_f_t_p_pipeline_minimal_response = SFTPPipelineMinimalResponse()
        elif mapping_value and mapping_value.casefold() == "S3".casefold():
            from .s3_pipeline_minimal_response import S3PipelineMinimalResponse

            result.s3_pipeline_minimal_response = S3PipelineMinimalResponse()
        elif mapping_value and mapping_value.casefold() == "ServiceNow".casefold():
            from .service_now_pipeline_minimal_response import ServiceNowPipelineMinimalResponse

            result.service_now_pipeline_minimal_response = ServiceNowPipelineMinimalResponse()
        elif mapping_value and mapping_value.casefold() == "WorkZone".casefold():
            from .work_zone_pipeline_minimal_response import WorkZonePipelineMinimalResponse

            result.work_zone_pipeline_minimal_response = WorkZonePipelineMinimalResponse()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .google_drive_pipeline_minimal_response import GoogleDrivePipelineMinimalResponse
        from .m_s_share_point_pipeline_minimal_response import MSSharePointPipelineMinimalResponse
        from .s3_pipeline_minimal_response import S3PipelineMinimalResponse
        from .service_now_pipeline_minimal_response import ServiceNowPipelineMinimalResponse
        from .s_d_m_pipeline_minimal_response import SDMPipelineMinimalResponse
        from .s_f_t_p_pipeline_minimal_response import SFTPPipelineMinimalResponse
        from .work_zone_pipeline_minimal_response import WorkZonePipelineMinimalResponse

        if self.google_drive_pipeline_minimal_response:
            return self.google_drive_pipeline_minimal_response.get_field_deserializers()
        if self.m_s_share_point_pipeline_minimal_response:
            return self.m_s_share_point_pipeline_minimal_response.get_field_deserializers()
        if self.s_d_m_pipeline_minimal_response:
            return self.s_d_m_pipeline_minimal_response.get_field_deserializers()
        if self.s_f_t_p_pipeline_minimal_response:
            return self.s_f_t_p_pipeline_minimal_response.get_field_deserializers()
        if self.s3_pipeline_minimal_response:
            return self.s3_pipeline_minimal_response.get_field_deserializers()
        if self.service_now_pipeline_minimal_response:
            return self.service_now_pipeline_minimal_response.get_field_deserializers()
        if self.work_zone_pipeline_minimal_response:
            return self.work_zone_pipeline_minimal_response.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.google_drive_pipeline_minimal_response:
            writer.write_object_value(None, self.google_drive_pipeline_minimal_response)
        elif self.m_s_share_point_pipeline_minimal_response:
            writer.write_object_value(None, self.m_s_share_point_pipeline_minimal_response)
        elif self.s_d_m_pipeline_minimal_response:
            writer.write_object_value(None, self.s_d_m_pipeline_minimal_response)
        elif self.s_f_t_p_pipeline_minimal_response:
            writer.write_object_value(None, self.s_f_t_p_pipeline_minimal_response)
        elif self.s3_pipeline_minimal_response:
            writer.write_object_value(None, self.s3_pipeline_minimal_response)
        elif self.service_now_pipeline_minimal_response:
            writer.write_object_value(None, self.service_now_pipeline_minimal_response)
        elif self.work_zone_pipeline_minimal_response:
            writer.write_object_value(None, self.work_zone_pipeline_minimal_response)
    

