from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .validation_error_ctx import ValidationError_ctx

@dataclass
class ValidationError(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The ctx property
    ctx: Optional[ValidationError_ctx] = None
    # The loc property
    loc: Optional[list[str]] = None
    # The msg property
    msg: Optional[str] = None
    # The type property
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ValidationError:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ValidationError
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ValidationError()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .validation_error_ctx import ValidationError_ctx

        from .validation_error_ctx import ValidationError_ctx

        fields: dict[str, Callable[[Any], None]] = {
            "ctx": lambda n : setattr(self, 'ctx', n.get_object_value(ValidationError_ctx)),
            "loc": lambda n : setattr(self, 'loc', n.get_collection_of_primitive_values(str)),
            "msg": lambda n : setattr(self, 'msg', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
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
        writer.write_object_value("ctx", self.ctx)
        writer.write_collection_of_primitive_values("loc", self.loc)
        writer.write_str_value("msg", self.msg)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

