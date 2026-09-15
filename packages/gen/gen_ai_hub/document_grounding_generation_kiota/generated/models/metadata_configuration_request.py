from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .metadata_configuration_request_data_repository_type import MetadataConfigurationRequest_dataRepositoryType
    from .metadata_configuration_request_labels import MetadataConfigurationRequest_labels

@dataclass
class MetadataConfigurationRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The data repository type for which this configuration is being created.
    data_repository_type: Optional[MetadataConfigurationRequest_dataRepositoryType] = None
    # Contains destination name containing credentials to access the data repository.
    destination_name: Optional[str] = None
    # If provided, must be a valid UUID. If not provided, a new UUID will be generated.
    id: Optional[str] = None
    # The includePaths property
    include_paths: Optional[list[str]] = None
    # The labels property
    labels: Optional[list[MetadataConfigurationRequest_labels]] = None
    # If provided, must be a valid string. If not provided, will be same as id.
    name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MetadataConfigurationRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MetadataConfigurationRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MetadataConfigurationRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .metadata_configuration_request_data_repository_type import MetadataConfigurationRequest_dataRepositoryType
        from .metadata_configuration_request_labels import MetadataConfigurationRequest_labels

        from .metadata_configuration_request_data_repository_type import MetadataConfigurationRequest_dataRepositoryType
        from .metadata_configuration_request_labels import MetadataConfigurationRequest_labels

        fields: dict[str, Callable[[Any], None]] = {
            "dataRepositoryType": lambda n : setattr(self, 'data_repository_type', n.get_enum_value(MetadataConfigurationRequest_dataRepositoryType)),
            "destinationName": lambda n : setattr(self, 'destination_name', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "includePaths": lambda n : setattr(self, 'include_paths', n.get_collection_of_primitive_values(str)),
            "labels": lambda n : setattr(self, 'labels', n.get_collection_of_object_values(MetadataConfigurationRequest_labels)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
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
        writer.write_enum_value("dataRepositoryType", self.data_repository_type)
        writer.write_str_value("destinationName", self.destination_name)
        writer.write_str_value("id", self.id)
        writer.write_collection_of_primitive_values("includePaths", self.include_paths)
        writer.write_collection_of_object_values("labels", self.labels)
        writer.write_str_value("name", self.name)
        writer.write_additional_data_value(self.additional_data)
    

