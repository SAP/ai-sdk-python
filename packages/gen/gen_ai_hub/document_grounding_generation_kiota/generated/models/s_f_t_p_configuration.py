from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .s_f_t_p_configuration_sftp import SFTPConfiguration_sftp

@dataclass
class SFTPConfiguration(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The cronExpression property
    cron_expression: Optional[str] = None
    # The destination property
    destination: Optional[str] = None
    # The sftp property
    sftp: Optional[SFTPConfiguration_sftp] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SFTPConfiguration:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SFTPConfiguration
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SFTPConfiguration()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .s_f_t_p_configuration_sftp import SFTPConfiguration_sftp

        from .s_f_t_p_configuration_sftp import SFTPConfiguration_sftp

        fields: dict[str, Callable[[Any], None]] = {
            "cronExpression": lambda n : setattr(self, 'cron_expression', n.get_str_value()),
            "destination": lambda n : setattr(self, 'destination', n.get_str_value()),
            "sftp": lambda n : setattr(self, 'sftp', n.get_object_value(SFTPConfiguration_sftp)),
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
        writer.write_object_value("sftp", self.sftp)
        writer.write_additional_data_value(self.additional_data)
    

