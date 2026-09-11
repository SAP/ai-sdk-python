from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieval_scoped_key_value_list_pair_scope import RetrievalScopedKeyValueListPair_scope

@dataclass
class RetrievalScopedKeyValueListPair(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    from .retrieval_scoped_key_value_list_pair_scope import RetrievalScopedKeyValueListPair_scope

    # The scope property
    scope: Optional[RetrievalScopedKeyValueListPair_scope] = RetrievalScopedKeyValueListPair_scope("document")
    # The key property
    key: Optional[str] = None
    # The value property
    value: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalScopedKeyValueListPair:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalScopedKeyValueListPair
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrievalScopedKeyValueListPair()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieval_scoped_key_value_list_pair_scope import RetrievalScopedKeyValueListPair_scope

        from .retrieval_scoped_key_value_list_pair_scope import RetrievalScopedKeyValueListPair_scope

        fields: dict[str, Callable[[Any], None]] = {
            "key": lambda n : setattr(self, 'key', n.get_str_value()),
            "scope": lambda n : setattr(self, 'scope', n.get_enum_value(RetrievalScopedKeyValueListPair_scope)),
            "value": lambda n : setattr(self, 'value', n.get_collection_of_primitive_values(str)),
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
        writer.write_str_value("key", self.key)
        writer.write_enum_value("scope", self.scope)
        writer.write_collection_of_primitive_values("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

