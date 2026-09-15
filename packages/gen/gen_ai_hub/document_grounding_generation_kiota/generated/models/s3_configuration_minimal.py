from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .s3_configuration_minimal_s3 import S3ConfigurationMinimal_s3

@dataclass
class S3ConfigurationMinimal(Parsable):
    # The s3 property
    s3: Optional[S3ConfigurationMinimal_s3] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> S3ConfigurationMinimal:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: S3ConfigurationMinimal
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return S3ConfigurationMinimal()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .s3_configuration_minimal_s3 import S3ConfigurationMinimal_s3

        from .s3_configuration_minimal_s3 import S3ConfigurationMinimal_s3

        fields: dict[str, Callable[[Any], None]] = {
            "s3": lambda n : setattr(self, 's3', n.get_object_value(S3ConfigurationMinimal_s3)),
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
        writer.write_object_value("s3", self.s3)
    

