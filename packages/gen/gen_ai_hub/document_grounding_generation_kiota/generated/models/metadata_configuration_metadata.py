from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .meta_data_key_value_pair_strict import MetaDataKeyValuePairStrict

@dataclass
class MetadataConfiguration_metadata(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The dataRepositoryMetadata property
    data_repository_metadata: Optional[list[MetaDataKeyValuePairStrict]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MetadataConfiguration_metadata:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MetadataConfiguration_metadata
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MetadataConfiguration_metadata()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .meta_data_key_value_pair_strict import MetaDataKeyValuePairStrict

        from .meta_data_key_value_pair_strict import MetaDataKeyValuePairStrict

        fields: dict[str, Callable[[Any], None]] = {
            "dataRepositoryMetadata": lambda n : setattr(self, 'data_repository_metadata', n.get_collection_of_object_values(MetaDataKeyValuePairStrict)),
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
        writer.write_collection_of_object_values("dataRepositoryMetadata", self.data_repository_metadata)
        writer.write_additional_data_value(self.additional_data)
    

