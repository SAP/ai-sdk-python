from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .service_now_config import ServiceNowConfig

@dataclass
class ServiceNowConfigurationStruct(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Optional cron expression for scheduling pipeline execution.Must represent an interval greater than 1 hour.
    cron_expression: Optional[str] = None
    # The destination property
    destination: Optional[str] = None
    # The metadataConfigId property
    metadata_config_id: Optional[str] = None
    # The serviceNow property
    service_now: Optional[ServiceNowConfig] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ServiceNowConfigurationStruct:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ServiceNowConfigurationStruct
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ServiceNowConfigurationStruct()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .service_now_config import ServiceNowConfig

        from .service_now_config import ServiceNowConfig

        fields: dict[str, Callable[[Any], None]] = {
            "cronExpression": lambda n : setattr(self, 'cron_expression', n.get_str_value()),
            "destination": lambda n : setattr(self, 'destination', n.get_str_value()),
            "metadataConfigId": lambda n : setattr(self, 'metadata_config_id', n.get_str_value()),
            "serviceNow": lambda n : setattr(self, 'service_now', n.get_object_value(ServiceNowConfig)),
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
        writer.write_str_value("cronExpression", self.cron_expression)
        writer.write_str_value("destination", self.destination)
        writer.write_str_value("metadataConfigId", self.metadata_config_id)
        writer.write_object_value("serviceNow", self.service_now)
        writer.write_additional_data_value(self.additional_data)
    

