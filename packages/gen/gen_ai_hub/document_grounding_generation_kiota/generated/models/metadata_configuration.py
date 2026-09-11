from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .metadata_configuration_metadata import MetadataConfiguration_metadata
    from .metadata_configuration_struct import MetadataConfigurationStruct
    from .metadata_configuration_type import MetadataConfiguration_type

@dataclass
class MetadataConfiguration(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The configuration property
    configuration: Optional[MetadataConfigurationStruct] = None
    # The metadata property
    metadata: Optional[MetadataConfiguration_metadata] = None
    # The type property
    type: Optional[MetadataConfiguration_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MetadataConfiguration:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MetadataConfiguration
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MetadataConfiguration()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .metadata_configuration_metadata import MetadataConfiguration_metadata
        from .metadata_configuration_struct import MetadataConfigurationStruct
        from .metadata_configuration_type import MetadataConfiguration_type

        from .metadata_configuration_metadata import MetadataConfiguration_metadata
        from .metadata_configuration_struct import MetadataConfigurationStruct
        from .metadata_configuration_type import MetadataConfiguration_type

        fields: dict[str, Callable[[Any], None]] = {
            "configuration": lambda n : setattr(self, 'configuration', n.get_object_value(MetadataConfigurationStruct)),
            "metadata": lambda n : setattr(self, 'metadata', n.get_object_value(MetadataConfiguration_metadata)),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(MetadataConfiguration_type)),
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
    

